"""Profiler: Automatic statistical profiling of dataframe columns."""

import statistics
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def detect_column_type(values: List[Any]) -> str:
    """Detect the data type of a column."""
    non_null_values = [v for v in values if v is not None and v != "" and str(v).upper() != "N/A"]

    if not non_null_values:
        return "unknown"

    # Try to detect numeric
    numeric_count = 0
    for v in non_null_values[:min(10, len(non_null_values))]:
        try:
            float(str(v))
            numeric_count += 1
        except (ValueError, TypeError):
            pass

    if numeric_count == len(non_null_values[:min(10, len(non_null_values))]):
        return "numeric"

    # Try to detect date
    date_count = 0
    for v in non_null_values[:min(5, len(non_null_values))]:
        try:
            datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            date_count += 1
        except (ValueError, TypeError):
            pass

    if date_count == len(non_null_values[:min(5, len(non_null_values))]):
        return "date"

    # Try to detect boolean
    bool_values = {"true", "false", "yes", "no", "1", "0"}
    bool_count = sum(1 for v in non_null_values if str(v).lower() in bool_values)
    if bool_count / len(non_null_values) > 0.8:
        return "boolean"

    return "string"


def calculate_numeric_stats(values: List[float]) -> Dict[str, Any]:
    """Calculate statistical metrics for numeric columns."""
    if not values:
        return {}

    sorted_values = sorted(values)
    n = len(values)

    stats = {
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / n,
        "median": sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2,
    }

    # Calculate standard deviation
    mean = stats["mean"]
    variance = sum((x - mean) ** 2 for x in values) / n
    stats["std"] = variance ** 0.5

    return stats


def detect_anomalies(values: List[float], threshold: float = 3.0) -> List[Tuple[int, float]]:
    """Detect anomalies using 3-sigma rule (z-score > threshold)."""
    if len(values) < 2:
        return []

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std = variance ** 0.5

    if std == 0:
        return []

    anomalies = []
    for i, value in enumerate(values):
        z_score = abs((value - mean) / std)
        if z_score > threshold:
            anomalies.append((i, value))

    return anomalies


def profile_column(name: str, values: List[Any]) -> Dict[str, Any]:
    """Profile a single column and return statistics."""
    total_count = len(values)
    null_count = sum(1 for v in values if v is None or v == "" or str(v).upper() == "N/A")
    non_null_count = total_count - null_count
    null_percentage = (null_count / total_count * 100) if total_count > 0 else 0

    # Cardinality (unique values)
    unique_values = set(v for v in values if v is not None and v != "" and str(v).upper() != "N/A")
    cardinality = len(unique_values)

    # Column type detection
    column_type = detect_column_type(values)

    # Top 10 most frequent values
    non_null_values = [v for v in values if v is not None and v != "" and str(v).upper() != "N/A"]
    value_counts = Counter(non_null_values)
    top_10 = value_counts.most_common(10)
    top_values = [{"value": str(v), "count": count} for v, count in top_10]

    profile = {
        "name": name,
        "type": column_type,
        "total_count": total_count,
        "null_count": null_count,
        "null_percentage": round(null_percentage, 2),
        "non_null_count": non_null_count,
        "cardinality": cardinality,
        "top_values": top_values,
    }

    # Distribution statistics for numeric columns
    anomalies = []
    if column_type == "numeric":
        try:
            numeric_values = []
            for v in values:
                if v is not None and v != "" and str(v).upper() != "N/A":
                    try:
                        numeric_values.append(float(v))
                    except (ValueError, TypeError):
                        pass

            if numeric_values:
                distribution = calculate_numeric_stats(numeric_values)
                profile["distribution"] = distribution

                # Anomaly detection (3-sigma)
                detected_anomalies = detect_anomalies(numeric_values, threshold=3.0)
                anomalies = [
                    {"index": idx, "value": val, "z_score": abs((val - distribution["mean"]) / distribution["std"])}
                    for idx, val in detected_anomalies
                ]
        except Exception:
            pass

    if anomalies:
        profile["anomalies"] = anomalies

    return profile


def profile_dataframe(df_dict: Dict[str, List[Any]]) -> Dict[str, Any]:
    """Profile an entire dataframe (represented as dict of columns)."""
    profiles = {}
    anomaly_list = []

    for column_name, column_values in df_dict.items():
        profile = profile_column(column_name, column_values)
        profiles[column_name] = profile

        # Collect anomalies
        if "anomalies" in profile:
            for anomaly in profile["anomalies"]:
                anomaly_list.append({
                    "column": column_name,
                    "index": anomaly["index"],
                    "value": anomaly["value"],
                    "z_score": anomaly["z_score"]
                })

    return {
        "columns": profiles,
        "anomalies": anomaly_list,
    }
