"""Validation script for Challenge 5: Data Quality Module."""

import ast
import json
import os
import sys


EXPECTED_FILES = [
    "src/data_quality/__init__.py",
    "src/data_quality/profiler.py",
    "src/data_quality/report.py",
    "src/data_quality/quality_gate.py",
]


def check_module_structure():
    """Check that the data_quality package exists with expected files."""
    issues = []
    for filepath in EXPECTED_FILES:
        if not os.path.exists(filepath):
            issues.append(f"MISSING: {filepath}")
    return issues


def check_profiler():
    """Check profiler.py has required profiling functions."""
    path = "src/data_quality/profiler.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()

    issues = []
    required_concepts = {
        "null": "null/missing value detection",
        "unique": "cardinality/unique value counting",
        "distribution": "distribution statistics (min/max/mean/std)",
    }
    # Check for at least basic profiling concepts
    content_lower = content.lower()
    for keyword, description in required_concepts.items():
        if keyword not in content_lower and keyword.replace("_", " ") not in content_lower:
            issues.append(f"profiler.py: missing {description} (keyword: '{keyword}')")

    # Check for statistical functions
    stat_keywords = ["mean", "median", "std", "min", "max", "average"]
    if not any(kw in content_lower for kw in stat_keywords):
        issues.append("profiler.py: no statistical calculations detected")

    return issues


def check_report_generation():
    """Check report.py generates JSON reports."""
    path = "src/data_quality/report.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()

    issues = []
    if "json" not in content:
        issues.append("report.py: no JSON handling detected")

    tree = ast.parse(content)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    if not any("report" in fn.lower() or "generate" in fn.lower() for fn in func_names):
        issues.append("report.py: no report generation function found")

    return issues


def check_quality_gates():
    """Check quality_gate.py implements threshold checks."""
    path = "src/data_quality/quality_gate.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()

    issues = []
    content_lower = content.lower()

    # Check for threshold checking
    threshold_keywords = ["threshold", "limit", "max_null", "completeness", "gate"]
    if not any(kw in content_lower for kw in threshold_keywords):
        issues.append("quality_gate.py: no threshold checking detected")

    # Check for blocking/raising behavior
    block_keywords = ["raise", "error", "block", "fail", "reject", "exception"]
    if not any(kw in content_lower for kw in block_keywords):
        issues.append("quality_gate.py: no pipeline blocking mechanism detected")

    return issues


def check_config_file():
    """Check that quality thresholds config file exists."""
    config_paths = [
        "config/quality_thresholds.json",
        "config/quality_thresholds.yaml",
        "config/quality_thresholds.yml",
        "config/quality_config.json",
        "config/quality_config.yaml",
    ]
    for path in config_paths:
        if os.path.exists(path):
            # Validate it's parseable
            if path.endswith(".json"):
                try:
                    with open(path, "r") as f:
                        json.load(f)
                    return []
                except json.JSONDecodeError as e:
                    return [f"Config file {path} is not valid JSON: {e}"]
            return []

    return ["No quality thresholds config file found in config/"]


def check_anomaly_detection():
    """Check for anomaly detection capability."""
    issues = []
    all_content = ""
    for root, dirs, files in os.walk("src/data_quality"):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r") as fh:
                    all_content += fh.read()

    content_lower = all_content.lower()
    anomaly_keywords = ["anomal", "outlier", "zscore", "z_score", "std", "deviation",
                        "iqr", "interquartile"]
    if not any(kw in content_lower for kw in anomaly_keywords):
        issues.append("No anomaly/outlier detection logic found")

    return issues


def check_syntax():
    """Check all Python files are syntactically valid."""
    issues = []
    for root, dirs, files in os.walk("src/data_quality"):
        for f in files:
            if not f.endswith(".py"):
                continue
            filepath = os.path.join(root, f)
            try:
                with open(filepath, "r") as fh:
                    ast.parse(fh.read())
            except SyntaxError as e:
                issues.append(f"SYNTAX ERROR in {filepath}: {e}")
    return issues


def main():
    print("=" * 60)
    print("Challenge 5 Validation: Data Quality Module")
    print("=" * 60)

    all_issues = []
    checks = [
        ("Module structure", check_module_structure),
        ("Profiler functions", check_profiler),
        ("Report generation", check_report_generation),
        ("Quality gates", check_quality_gates),
        ("Config file", check_config_file),
        ("Anomaly detection", check_anomaly_detection),
        ("Syntax validity", check_syntax),
    ]

    for name, check_fn in checks:
        issues = check_fn()
        status = "PASS" if not issues else "FAIL"
        print(f"\n[{status}] {name}")
        for issue in issues:
            print(f"  - {issue}")
        all_issues.extend(issues)

    print("\n" + "=" * 60)
    if all_issues:
        print(f"RESULT: FAIL ({len(all_issues)} issues found)")
        sys.exit(1)
    else:
        print("RESULT: ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
