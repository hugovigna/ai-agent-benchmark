"""Data export: write results to CSV, JSON, and Parquet."""

import pandas as pd
import json
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from config.settings import PIPELINE

logger = logging.getLogger(__name__)


def write_csv(df: pd.DataFrame, filepath: str, index: bool = False) -> str:
    """Export DataFrame to CSV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=index)
    logger.info(f"Wrote {len(df)} rows to {filepath}")
    return filepath


def write_json(data: Any, filepath: str) -> str:
    """Export data (DataFrame or dict) to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if isinstance(data, pd.DataFrame):
        data.to_json(filepath, orient="records", indent=2)
    else:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
    return filepath


def write_parquet(df: pd.DataFrame, filepath: str) -> str:
    """Export DataFrame to Parquet file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_parquet(filepath, index=False)
    return filepath


class ReportGenerator:
    """Generates summary and quality reports for exported data."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or PIPELINE["output_dir"]
        self._reports: Dict[str, str] = {}

    def create_summary(self, df: pd.DataFrame, name: str) -> dict:
        """Create a statistical summary of a DataFrame."""
        summary = {
            "name": name,
            "generated_at": datetime.now().isoformat(),
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": {}
        }
        for col in df.columns:
            info = {"dtype": str(df[col].dtype), "nulls": int(df[col].isnull().sum())}
            if pd.api.types.is_numeric_dtype(df[col]):
                info["mean"] = float(df[col].mean())
                info["std"] = float(df[col].std())
            summary["columns"][col] = info
        return summary

    def save_report(self, report: dict, filename: str) -> str:
        """Write a report dict to a JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        path = write_json(report, filepath)
        self._reports[filename] = path
        return path

    def list_reports(self) -> Dict[str, str]:
        return self._reports.copy()
