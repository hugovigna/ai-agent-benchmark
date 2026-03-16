"""Validation script for Challenge 4: Checkpointing System."""

import ast
import os
import sys


def check_checkpoint_module():
    """Check that a checkpoint module/class exists."""
    issues = []
    # Look for checkpoint-related files
    checkpoint_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py") and "checkpoint" in f.lower():
                checkpoint_files.append(os.path.join(root, f))

    if not checkpoint_files:
        # Check if checkpointing is added inline in long_pipeline.py
        if os.path.exists("src/long_pipeline.py"):
            with open("src/long_pipeline.py", "r") as f:
                content = f.read()
            if "checkpoint" not in content.lower():
                issues.append("No checkpoint module or checkpoint logic found")
        else:
            issues.append("No checkpoint file or long_pipeline.py found")
    return issues


def check_save_checkpoint():
    """Check that checkpoints are saved after each step."""
    issues = []
    py_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    all_content = ""
    for pf in py_files:
        with open(pf, "r") as f:
            all_content += f.read()

    if "save" not in all_content.lower() or "checkpoint" not in all_content.lower():
        issues.append("No save_checkpoint or similar function found")

    # Check for JSON serialization
    if "json" not in all_content:
        issues.append("No JSON serialization detected for checkpoints")

    return issues


def check_resume_logic():
    """Check that resume/recovery logic exists."""
    issues = []
    pipeline_path = "src/long_pipeline.py"
    if not os.path.exists(pipeline_path):
        return ["src/long_pipeline.py not found"]

    with open(pipeline_path, "r") as f:
        content = f.read()

    resume_keywords = ["resume", "recover", "restore", "load_checkpoint", "last_step",
                        "completed_step", "skip"]
    if not any(kw in content.lower() for kw in resume_keywords):
        issues.append("No resume/recovery logic detected in long_pipeline.py")

    return issues


def check_cleanup():
    """Check that checkpoints are cleaned up after success."""
    issues = []
    py_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    all_content = ""
    for pf in py_files:
        with open(pf, "r") as f:
            all_content += f.read()

    cleanup_keywords = ["clean", "remove", "delete", "unlink", "rmtree", "cleanup"]
    if not any(kw in all_content.lower() for kw in cleanup_keywords):
        issues.append("No checkpoint cleanup logic detected")

    return issues


def check_force_restart():
    """Check that a force restart option exists."""
    issues = []
    pipeline_path = "src/long_pipeline.py"
    if not os.path.exists(pipeline_path):
        return ["src/long_pipeline.py not found"]

    with open(pipeline_path, "r") as f:
        content = f.read()

    force_keywords = ["force_restart", "force-restart", "force", "fresh_start",
                       "ignore_checkpoint", "no_resume"]
    if not any(kw in content.lower() for kw in force_keywords):
        issues.append("No force restart option detected")

    return issues


def check_syntax():
    """Check all Python files are syntactically valid."""
    issues = []
    for root, dirs, files in os.walk("src"):
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
    print("Challenge 4 Validation: Checkpointing System")
    print("=" * 60)

    all_issues = []
    checks = [
        ("Checkpoint module exists", check_checkpoint_module),
        ("Save checkpoint logic", check_save_checkpoint),
        ("Resume/recovery logic", check_resume_logic),
        ("Cleanup after success", check_cleanup),
        ("Force restart option", check_force_restart),
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
