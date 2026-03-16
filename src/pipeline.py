"""Main data pipeline - processes raw data end to end."""

import os
import csv
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


def run_pipeline(input_dir, output_dir):
    """Run the full data pipeline from extraction to loading."""
    start_time = time.time()
    logger.info("Pipeline started at %s", datetime.now().isoformat())

    # ============================================================
    # STEP 1: Discover source files
    # ============================================================
    source_files = []
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.endswith(".csv") or f.endswith(".json"):
                full_path = os.path.join(root, f)
                file_size = os.path.getsize(full_path)
                source_files.append({
                    "path": full_path,
                    "name": f,
                    "size": file_size,
                    "type": f.split(".")[-1],
                })
    logger.info("Discovered %d source files", len(source_files))
    if not source_files:
        logger.warning("No source files found in %s", input_dir)
        return {"status": "NO_DATA", "records": 0}

    # ============================================================
    # STEP 2: Read and parse CSV files
    # ============================================================
    csv_records = []
    for file_info in source_files:
        if file_info["type"] != "csv":
            continue
        try:
            with open(file_info["path"], "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    row["_source_file"] = file_info["name"]
                    row["_ingested_at"] = datetime.now().isoformat()
                    csv_records.append(row)
        except Exception as e:
            logger.error("Failed to read CSV %s: %s", file_info["path"], e)
    logger.info("Parsed %d records from CSV files", len(csv_records))

    # ============================================================
    # STEP 3: Read and parse JSON files
    # ============================================================
    json_records = []
    for file_info in source_files:
        if file_info["type"] != "json":
            continue
        try:
            with open(file_info["path"], "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    for record in data:
                        record["_source_file"] = file_info["name"]
                        record["_ingested_at"] = datetime.now().isoformat()
                        json_records.append(record)
                elif isinstance(data, dict):
                    data["_source_file"] = file_info["name"]
                    data["_ingested_at"] = datetime.now().isoformat()
                    json_records.append(data)
        except Exception as e:
            logger.error("Failed to read JSON %s: %s", file_info["path"], e)
    logger.info("Parsed %d records from JSON files", len(json_records))

    # ============================================================
    # STEP 4: Merge all records
    # ============================================================
    all_records = csv_records + json_records
    logger.info("Total raw records: %d", len(all_records))

    # ============================================================
    # STEP 5: Deduplicate records
    # ============================================================
    seen_hashes = set()
    unique_records = []
    duplicate_count = 0
    for record in all_records:
        record_str = json.dumps(record, sort_keys=True, default=str)
        record_hash = hashlib.md5(record_str.encode()).hexdigest()
        if record_hash not in seen_hashes:
            seen_hashes.add(record_hash)
            record["_hash"] = record_hash
            unique_records.append(record)
        else:
            duplicate_count += 1
    logger.info("Removed %d duplicates, %d unique records remain",
                duplicate_count, len(unique_records))

    # ============================================================
    # STEP 6: Clean and normalize fields
    # ============================================================
    cleaned_records = []
    for record in unique_records:
        cleaned = {}
        for key, value in record.items():
            clean_key = key.strip().lower().replace(" ", "_").replace("-", "_")
            if isinstance(value, str):
                value = value.strip()
                if value.lower() in ("null", "none", "n/a", "na", ""):
                    value = None
                elif value.replace(".", "").replace("-", "").isdigit():
                    try:
                        value = float(value) if "." in value else int(value)
                    except ValueError:
                        pass
            cleaned[clean_key] = value
        cleaned_records.append(cleaned)
    logger.info("Cleaned %d records", len(cleaned_records))

    # ============================================================
    # STEP 7: Validate required fields
    # ============================================================
    required_fields = ["id", "timestamp", "value"]
    valid_records = []
    invalid_records = []
    for record in cleaned_records:
        missing = [f for f in required_fields if f not in record or record[f] is None]
        if missing:
            record["_validation_errors"] = missing
            invalid_records.append(record)
        else:
            valid_records.append(record)
    logger.info("Validation: %d valid, %d invalid records",
                len(valid_records), len(invalid_records))

    # ============================================================
    # STEP 8: Enrich records with computed fields
    # ============================================================
    enriched_records = []
    for record in valid_records:
        try:
            if "timestamp" in record and record["timestamp"]:
                ts = str(record["timestamp"])
                if ts.isdigit():
                    dt = datetime.fromtimestamp(int(ts))
                else:
                    dt = datetime.fromisoformat(ts)
                record["_date"] = dt.strftime("%Y-%m-%d")
                record["_hour"] = dt.hour
                record["_day_of_week"] = dt.strftime("%A")
                record["_is_weekend"] = dt.weekday() >= 5
        except Exception as e:
            logger.warning("Failed to parse timestamp for record %s: %s",
                           record.get("id"), e)
            record["_date"] = None
            record["_hour"] = None
            record["_day_of_week"] = None
            record["_is_weekend"] = None

        if "value" in record and record["value"] is not None:
            try:
                val = float(record["value"])
                record["_value_bucket"] = (
                    "low" if val < 10
                    else "medium" if val < 100
                    else "high" if val < 1000
                    else "very_high"
                )
            except (ValueError, TypeError):
                record["_value_bucket"] = "unknown"

        record["_processed_at"] = datetime.now().isoformat()
        enriched_records.append(record)
    logger.info("Enriched %d records", len(enriched_records))

    # ============================================================
    # STEP 9: Aggregate statistics
    # ============================================================
    stats = {
        "total_records": len(enriched_records),
        "by_date": defaultdict(int),
        "by_bucket": defaultdict(int),
        "by_source": defaultdict(int),
        "value_sum": 0,
        "value_count": 0,
        "value_min": float("inf"),
        "value_max": float("-inf"),
    }
    for record in enriched_records:
        date = record.get("_date", "unknown")
        stats["by_date"][date] += 1
        bucket = record.get("_value_bucket", "unknown")
        stats["by_bucket"][bucket] += 1
        source = record.get("_source_file", "unknown")
        stats["by_source"][source] += 1
        try:
            val = float(record.get("value", 0))
            stats["value_sum"] += val
            stats["value_count"] += 1
            stats["value_min"] = min(stats["value_min"], val)
            stats["value_max"] = max(stats["value_max"], val)
        except (ValueError, TypeError):
            pass
    if stats["value_count"] > 0:
        stats["value_mean"] = stats["value_sum"] / stats["value_count"]
    else:
        stats["value_mean"] = 0
    stats["by_date"] = dict(stats["by_date"])
    stats["by_bucket"] = dict(stats["by_bucket"])
    stats["by_source"] = dict(stats["by_source"])
    logger.info("Aggregation complete: %d records processed", stats["total_records"])

    # ============================================================
    # STEP 10: Write output files
    # ============================================================
    os.makedirs(output_dir, exist_ok=True)

    # Write enriched records
    output_path = os.path.join(output_dir, "enriched_data.json")
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(enriched_records, fh, indent=2, default=str)
    logger.info("Wrote enriched data to %s", output_path)

    # Write invalid records
    invalid_path = os.path.join(output_dir, "invalid_records.json")
    with open(invalid_path, "w", encoding="utf-8") as fh:
        json.dump(invalid_records, fh, indent=2, default=str)
    logger.info("Wrote %d invalid records to %s", len(invalid_records), invalid_path)

    # Write statistics
    stats_path = os.path.join(output_dir, "pipeline_stats.json")
    with open(stats_path, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, default=str)
    logger.info("Wrote pipeline stats to %s", stats_path)

    # Write manifest
    elapsed = time.time() - start_time
    manifest = {
        "pipeline_run": datetime.now().isoformat(),
        "input_dir": input_dir,
        "output_dir": output_dir,
        "source_files": len(source_files),
        "total_raw_records": len(all_records),
        "duplicates_removed": duplicate_count,
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "enriched_records": len(enriched_records),
        "elapsed_seconds": round(elapsed, 2),
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    logger.info("Wrote manifest to %s", manifest_path)

    logger.info("Pipeline completed in %.2f seconds", elapsed)
    return manifest


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = run_pipeline("./data/raw", "./data/output")
    print(json.dumps(result, indent=2))
