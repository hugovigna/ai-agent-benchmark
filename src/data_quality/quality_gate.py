"""Quality Gate: Check quality thresholds and block pipeline if needed."""

import sys
from typing import Any, Dict, List, Tuple

from .config import load_config


class QualityCheckError(Exception):
    """Raised when quality checks fail and pipeline must be blocked."""
    pass


def check_quality_gates(
    profile: Dict[str, Any],
    config_path: str = "config/quality_thresholds.json"
) -> Tuple[bool, List[str]]:
    """Check if data meets quality thresholds.

    Args:
        profile: Profiling results from profiler.profile_dataframe()
        config_path: Path to quality thresholds configuration

    Returns:
        Tuple of (passed: bool, messages: List[str])
        If passed is False, messages contain details about what failed

    Raises:
        QualityCheckError: If quality gates fail (blocking error)
    """
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        # Fallback to defaults if config not found
        from .config import DEFAULT_THRESHOLDS
        config = DEFAULT_THRESHOLDS

    max_null_percentage = config.get("max_null_percentage", 10.0)
    min_completeness = config.get("min_completeness", 90.0)
    max_duplicate_percentage = config.get("max_duplicate_percentage", 5.0)

    errors = []
    warnings = []

    if not profile.get("columns"):
        raise QualityCheckError("No profiling data available")

    # Check 1: Max null percentage per column
    for col_name, col_profile in profile["columns"].items():
        null_percentage = col_profile.get("null_percentage", 0)
        if null_percentage > max_null_percentage:
            errors.append(
                f"Column '{col_name}': null percentage {null_percentage}% exceeds limit {max_null_percentage}%"
            )

    # Check 2: Min completeness (average non-null percentage across all columns)
    total_cells = 0
    non_null_cells = 0
    for col_profile in profile["columns"].values():
        total_count = col_profile.get("total_count", 0)
        null_count = col_profile.get("null_count", 0)
        total_cells += total_count
        non_null_cells += total_count - null_count

    completeness = (non_null_cells / total_cells * 100) if total_cells > 0 else 0
    if completeness < min_completeness:
        errors.append(
            f"Dataset completeness {completeness:.1f}% is below minimum {min_completeness}%"
        )

    # Check 3: Detect duplicates (rows that appear multiple times)
    # Note: This is a simplified check based on column cardinality
    for col_name, col_profile in profile["columns"].items():
        cardinality = col_profile.get("cardinality", 0)
        total_count = col_profile.get("total_count", 0)
        if total_count > 0:
            duplicate_percentage = ((total_count - cardinality) / total_count * 100)
            if duplicate_percentage > max_duplicate_percentage:
                warnings.append(
                    f"Column '{col_name}': duplicate percentage {duplicate_percentage:.1f}% exceeds limit {max_duplicate_percentage}%"
                )

    # If there are errors, raise exception to block pipeline
    if errors:
        error_message = "Quality gate checks failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise QualityCheckError(error_message)

    # Return success with any warnings
    messages = warnings
    return True, messages


def check_quality_gates_safe(
    profile: Dict[str, Any],
    config_path: str = "config/quality_thresholds.json",
    exit_on_failure: bool = False
) -> bool:
    """Wrapper for check_quality_gates with optional exit behavior.

    Args:
        profile: Profiling results
        config_path: Path to configuration
        exit_on_failure: If True, exit process on failure; otherwise just return False

    Returns:
        True if all checks pass, False otherwise
    """
    try:
        passed, messages = check_quality_gates(profile, config_path)
        if messages:
            for msg in messages:
                print(f"WARNING: {msg}", file=sys.stderr)
        return passed
    except QualityCheckError as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}", file=sys.stderr)
        if exit_on_failure:
            sys.exit(1)
        return False
