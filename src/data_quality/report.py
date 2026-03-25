"""Report: Generate structured JSON report from profiling results."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def calculate_quality_score(profile: Dict[str, Any]) -> float:
    """Calculate overall quality score (0-100) based on profiling results."""
    if not profile.get("columns"):
        return 0.0

    columns = profile["columns"]
    scores = []

    for column_name, col_profile in columns.items():
        # Start with 100
        score = 100.0

        # Deduct points for nullness
        null_percentage = col_profile.get("null_percentage", 0)
        score -= min(50, null_percentage * 5)  # Max 50 points for nulls

        # Deduct points for anomalies
        anomalies = col_profile.get("anomalies", [])
        if anomalies:
            score -= min(25, len(anomalies) * 2)  # Max 25 points for anomalies

        # Ensure score is in 0-100 range
        score = max(0, min(100, score))
        scores.append(score)

    # Average score across all columns
    overall_score = sum(scores) / len(scores) if scores else 0.0
    return round(overall_score, 1)


def generate_report(
    profile: Dict[str, Any],
    source: str = "unknown",
    total_records: Optional[int] = None
) -> str:
    """Generate a structured JSON report from profiling results.

    Args:
        profile: Profiling results from profiler.profile_dataframe()
        source: Source of the data (e.g., filename)
        total_records: Total number of records (if None, inferred from profile)

    Returns:
        JSON string representation of the report
    """
    # Determine total records
    if total_records is None and profile.get("columns"):
        first_column = next(iter(profile["columns"].values()))
        total_records = first_column.get("total_count", 0)
    else:
        total_records = total_records or 0

    # Calculate quality score
    quality_score = calculate_quality_score(profile)

    # Build the report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "total_records": total_records,
        "quality_score": quality_score,
        "columns": profile.get("columns", {}),
        "anomalies": profile.get("anomalies", []),
    }

    return json.dumps(report, indent=2, default=str)


def generate_report_dict(
    profile: Dict[str, Any],
    source: str = "unknown",
    total_records: Optional[int] = None
) -> Dict[str, Any]:
    """Generate a structured report as a dictionary (non-serialized version).

    Args:
        profile: Profiling results from profiler.profile_dataframe()
        source: Source of the data (e.g., filename)
        total_records: Total number of records (if None, inferred from profile)

    Returns:
        Dictionary representation of the report
    """
    # Determine total records
    if total_records is None and profile.get("columns"):
        first_column = next(iter(profile["columns"].values()))
        total_records = first_column.get("total_count", 0)
    else:
        total_records = total_records or 0

    # Calculate quality score
    quality_score = calculate_quality_score(profile)

    # Build the report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "total_records": total_records,
        "quality_score": quality_score,
        "columns": profile.get("columns", {}),
        "anomalies": profile.get("anomalies", []),
    }

    return report
