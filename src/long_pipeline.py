"""Long-running pipeline with 10 sequential steps — no checkpointing."""

import os
import json
import time
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def step_01_fetch_sources(context):
    """Fetch data from multiple external sources."""
    logger.info("Step 1/10: Fetching sources...")
    time.sleep(0.5)  # Simulate network I/O
    context["sources"] = [
        {"name": "crm", "records": random.randint(1000, 5000)},
        {"name": "erp", "records": random.randint(2000, 8000)},
        {"name": "web_analytics", "records": random.randint(5000, 20000)},
    ]
    context["raw_count"] = sum(s["records"] for s in context["sources"])
    logger.info("Fetched %d total records from %d sources",
                context["raw_count"], len(context["sources"]))
    return context


def step_02_validate_schemas(context):
    """Validate that all source schemas match expectations."""
    logger.info("Step 2/10: Validating schemas...")
    time.sleep(0.3)
    expected_fields = {"id", "timestamp", "value", "category"}
    context["schema_valid"] = True
    for source in context["sources"]:
        source["schema_ok"] = True  # Simulated
    logger.info("All schemas validated successfully")
    return context


def step_03_deduplicate(context):
    """Remove duplicate records across sources."""
    logger.info("Step 3/10: Deduplicating...")
    time.sleep(0.4)
    dup_rate = random.uniform(0.05, 0.15)
    context["duplicates_removed"] = int(context["raw_count"] * dup_rate)
    context["deduped_count"] = context["raw_count"] - context["duplicates_removed"]
    logger.info("Removed %d duplicates", context["duplicates_removed"])
    return context


def step_04_clean_data(context):
    """Clean and normalize data fields."""
    logger.info("Step 4/10: Cleaning data...")
    time.sleep(0.6)
    context["null_filled"] = random.randint(50, 500)
    context["format_fixed"] = random.randint(100, 1000)
    context["clean_count"] = context["deduped_count"]
    logger.info("Filled %d nulls, fixed %d format issues",
                context["null_filled"], context["format_fixed"])
    return context


def step_05_apply_business_rules(context):
    """Apply business rules and transformations."""
    logger.info("Step 5/10: Applying business rules...")
    time.sleep(0.5)
    reject_rate = random.uniform(0.01, 0.05)
    context["rejected_by_rules"] = int(context["clean_count"] * reject_rate)
    context["rules_passed"] = context["clean_count"] - context["rejected_by_rules"]
    logger.info("Applied rules: %d passed, %d rejected",
                context["rules_passed"], context["rejected_by_rules"])
    return context


def step_06_enrich_external(context):
    """Enrich records with external reference data."""
    logger.info("Step 6/10: Enriching with external data...")
    time.sleep(0.8)  # Simulate slow external API
    context["enriched_count"] = context["rules_passed"]
    context["enrichment_fields_added"] = ["geo_region", "customer_segment", "risk_score"]
    logger.info("Enriched %d records with %d fields",
                context["enriched_count"], len(context["enrichment_fields_added"]))
    return context


def step_07_compute_aggregates(context):
    """Compute aggregate metrics and KPIs."""
    logger.info("Step 7/10: Computing aggregates...")
    time.sleep(0.4)
    context["aggregates"] = {
        "total_value": round(random.uniform(100000, 999999), 2),
        "avg_value": round(random.uniform(10, 500), 2),
        "category_counts": {"A": random.randint(100, 1000),
                            "B": random.randint(100, 1000),
                            "C": random.randint(100, 1000)},
    }
    logger.info("Computed aggregates: total_value=%.2f", context["aggregates"]["total_value"])
    return context


def step_08_generate_reports(context):
    """Generate summary reports."""
    logger.info("Step 8/10: Generating reports...")
    time.sleep(0.3)
    context["reports"] = [
        "daily_summary.json",
        "category_breakdown.json",
        "anomaly_report.json",
    ]
    logger.info("Generated %d reports", len(context["reports"]))
    return context


def step_09_load_to_warehouse(context):
    """Load processed data into the data warehouse."""
    logger.info("Step 9/10: Loading to warehouse...")
    time.sleep(0.7)  # Simulate bulk insert
    context["loaded_count"] = context["enriched_count"]
    context["load_table"] = "analytics.fact_events"
    logger.info("Loaded %d records to %s",
                context["loaded_count"], context["load_table"])
    return context


def step_10_notify_completion(context):
    """Send completion notifications."""
    logger.info("Step 10/10: Sending notifications...")
    time.sleep(0.2)
    context["notifications_sent"] = ["slack", "email"]
    context["pipeline_status"] = "SUCCESS"
    context["completed_at"] = datetime.now().isoformat()
    logger.info("Pipeline completed successfully")
    return context


PIPELINE_STEPS = [
    step_01_fetch_sources,
    step_02_validate_schemas,
    step_03_deduplicate,
    step_04_clean_data,
    step_05_apply_business_rules,
    step_06_enrich_external,
    step_07_compute_aggregates,
    step_08_generate_reports,
    step_09_load_to_warehouse,
    step_10_notify_completion,
]


def run_long_pipeline():
    """Run the full 10-step pipeline sequentially with no checkpointing.

    If any step fails, the entire pipeline must be restarted from scratch.
    """
    start_time = time.time()
    context = {
        "pipeline_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "started_at": datetime.now().isoformat(),
    }
    logger.info("Starting pipeline %s", context["pipeline_id"])

    for i, step_fn in enumerate(PIPELINE_STEPS, 1):
        try:
            context = step_fn(context)
        except Exception as e:
            logger.error("Pipeline failed at step %d/%d (%s): %s",
                         i, len(PIPELINE_STEPS), step_fn.__name__, e)
            context["pipeline_status"] = "FAILED"
            context["failed_step"] = i
            context["error"] = str(e)
            raise

    elapsed = time.time() - start_time
    context["elapsed_seconds"] = round(elapsed, 2)
    logger.info("Full pipeline completed in %.2f seconds", elapsed)
    return context


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = run_long_pipeline()
    print(json.dumps(result, indent=2, default=str))
