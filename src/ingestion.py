"""Data ingestion: reads from CSV, JSON, and API sources."""

import pandas as pd
import json
import os
import logging
from typing import List, Optional

from src.models import Record
from config.settings import PIPELINE

logger = logging.getLogger(__name__)


def read_csv_source(filepath: str, separator: str = ",") -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV source not found: {filepath}")
    df = pd.read_csv(filepath, sep=separator)
    logger.info(f"Ingested {len(df)} rows from CSV: {filepath}")
    return df


def read_json_source(filepath: str) -> List[dict]:
    """Read a JSON file and return list of records."""
    with open(filepath, "r") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    logger.info(f"Ingested {len(data)} records from JSON: {filepath}")
    return data


def parse_records(raw_data: List[dict], source_name: str) -> List[Record]:
    """Convert raw dicts to Record objects, skipping invalid entries."""
    from datetime import datetime
    records = []
    for item in raw_data:
        try:
            rec = Record(
                id=str(item.get("id", "")),
                timestamp=datetime.fromisoformat(item.get("timestamp", datetime.now().isoformat())),
                source=source_name,
                payload=item,
                tags=item.get("tags", [])
            )
            if rec.is_valid():
                records.append(rec)
        except (ValueError, KeyError) as e:
            logger.warning(f"Skipping invalid record: {e}")
    return records


class IngestionPipeline:
    """Orchestrates data ingestion from multiple sources."""

    def __init__(self, sources: List[str], batch_size: Optional[int] = None):
        self.sources = sources
        self.batch_size = batch_size or PIPELINE["batch_size"]
        self._ingested = []

    def run(self) -> pd.DataFrame:
        frames = []
        for src in self.sources:
            if src.endswith(".csv"):
                frames.append(read_csv_source(src))
            elif src.endswith(".json"):
                data = read_json_source(src)
                frames.append(pd.DataFrame(data))
            else:
                logger.warning(f"Unsupported source format: {src}")
        if not frames:
            return pd.DataFrame()
        result = pd.concat(frames, ignore_index=True)
        self._ingested = self.sources.copy()
        return result

    def get_stats(self) -> dict:
        return {
            "sources_processed": len(self._ingested),
            "total_sources": len(self.sources),
            "batch_size": self.batch_size
        }
