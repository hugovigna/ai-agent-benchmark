"""Config: Load and manage quality thresholds configuration."""

import json
import os
from typing import Any, Dict


# Default thresholds
DEFAULT_THRESHOLDS = {
    "max_null_percentage": 10.0,
    "min_completeness": 90.0,
    "max_duplicate_percentage": 5.0,
    "anomaly_threshold": 3.0,
}


def load_config(config_path: str = "config/quality_thresholds.json") -> Dict[str, Any]:
    """Load quality thresholds configuration from a JSON file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary of quality thresholds

    Raises:
        FileNotFoundError: If config file is not found
        json.JSONDecodeError: If config file is not valid JSON
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    # Merge with defaults (user config overrides defaults)
    thresholds = DEFAULT_THRESHOLDS.copy()
    if "thresholds" in config:
        thresholds.update(config["thresholds"])
    else:
        thresholds.update(config)

    return thresholds


def get_default_config() -> Dict[str, Any]:
    """Get default quality thresholds."""
    return DEFAULT_THRESHOLDS.copy()
