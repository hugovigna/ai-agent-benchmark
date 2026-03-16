"""Validation script for Challenge 3: Pipeline Refactoring."""

import ast
import os
import sys
import importlib.util


EXPECTED_MODULES = [
    "src/pipeline/__init__.py",
    "src/pipeline/extract.py",
    "src/pipeline/transform.py",
    "src/pipeline/load.py",
]


def check_package_structure():
    """Check that the pipeline package exists with expected modules."""
    issues = []
    if os.path.exists("src/pipeline.py"):
        issues.append("src/pipeline.py still exists (should be replaced by src/pipeline/)")
    for module_path in EXPECTED_MODULES:
        if not os.path.exists(module_path):
            issues.append(f"MISSING: {module_path}")
    return issues


def check_extract_module():
    """Check extract.py has file discovery and parsing functions."""
    path = "src/pipeline/extract.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    issues = []
    if not any("discover" in fn or "source" in fn or "find" in fn for fn in func_names):
        issues.append("extract.py: no file discovery function found")
    if not any("csv" in fn.lower() or "parse" in fn.lower() or "read" in fn.lower() for fn in func_names):
        issues.append("extract.py: no CSV/JSON parsing function found")
    return issues


def check_transform_module():
    """Check transform.py has cleaning and transformation functions."""
    path = "src/pipeline/transform.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    issues = []
    expected_concepts = ["dedup", "clean", "valid", "enrich"]
    for concept in expected_concepts:
        if not any(concept in fn.lower() for fn in func_names):
            issues.append(f"transform.py: no function related to '{concept}'")
    return issues


def check_load_module():
    """Check load.py has output writing functions."""
    path = "src/pipeline/load.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    issues = []
    if not any("write" in fn.lower() or "save" in fn.lower() or "load" in fn.lower() or "output" in fn.lower() for fn in func_names):
        issues.append("load.py: no output/write function found")
    return issues


def check_logging_present():
    """Check that logging is used in all modules."""
    issues = []
    for module_path in EXPECTED_MODULES:
        if not os.path.exists(module_path):
            continue
        with open(module_path, "r") as f:
            content = f.read()
        if "logging" not in content and "logger" not in content:
            issues.append(f"{module_path}: no logging detected")
    return issues


def check_orchestrator():
    """Check that __init__.py orchestrates the pipeline."""
    path = "src/pipeline/__init__.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()
    issues = []
    if "extract" not in content:
        issues.append("__init__.py: does not import/use extract module")
    if "transform" not in content:
        issues.append("__init__.py: does not import/use transform module")
    if "load" not in content:
        issues.append("__init__.py: does not import/use load module")
    return issues


def check_syntax():
    """Check all Python files are syntactically valid."""
    issues = []
    for module_path in EXPECTED_MODULES:
        if not os.path.exists(module_path):
            continue
        try:
            with open(module_path, "r") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            issues.append(f"SYNTAX ERROR in {module_path}: {e}")
    return issues


def main():
    print("=" * 60)
    print("Challenge 3 Validation: Pipeline Refactoring")
    print("=" * 60)

    all_issues = []
    checks = [
        ("Package structure", check_package_structure),
        ("Extract module", check_extract_module),
        ("Transform module", check_transform_module),
        ("Load module", check_load_module),
        ("Logging present", check_logging_present),
        ("Orchestrator", check_orchestrator),
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
