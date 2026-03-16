"""Validation script for Challenge 2: Hardcoded Credentials."""

import ast
import os
import sys
import re


CREDENTIAL_PATTERNS = [
    r"SuperSecret123!",
    r"sk-proj-a8f3k29d4m5n6p7q8r9s0t1u2v3w4x5y6z",
    r"whsec_MIIEvgIBADANBgkqhkiG9w0BAQEFAASC",
    r"AKIAIOSFODNN7EXAMPLE",
    r"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    r"hooks\.slack\.com/services/T0123456789",
    r"gmail_app_password_abcd1234efgh",
]

TARGET_FILES = [
    "src/db_connector.py",
    "src/api_client.py",
    "src/cloud_storage.py",
    "src/notification.py",
]


def check_no_hardcoded_creds():
    """Check that no hardcoded credentials remain."""
    issues = []
    for filepath in TARGET_FILES:
        if not os.path.exists(filepath):
            issues.append(f"MISSING: {filepath}")
            continue
        with open(filepath, "r") as f:
            content = f.read()
        for pattern in CREDENTIAL_PATTERNS:
            if pattern in content:
                issues.append(f"HARDCODED CRED in {filepath}: found '{pattern[:20]}...'")
    return issues


def check_env_example():
    """Check that .env.example exists with required variables."""
    if not os.path.exists(".env.example"):
        return ["MISSING: .env.example file"]
    with open(".env.example", "r") as f:
        content = f.read()
    expected_vars = ["DB_PASSWORD", "API_KEY", "AWS_ACCESS_KEY", "SLACK_WEBHOOK"]
    missing = [v for v in expected_vars if v not in content]
    if missing:
        return [f".env.example missing variables: {missing}"]
    return []


def check_gitignore():
    """Check that .gitignore excludes .env."""
    if not os.path.exists(".gitignore"):
        return ["MISSING: .gitignore file"]
    with open(".gitignore", "r") as f:
        content = f.read()
    if ".env" not in content:
        return [".gitignore does not exclude .env"]
    return []


def check_dotenv_usage():
    """Check that python-dotenv is used in target files."""
    issues = []
    for filepath in TARGET_FILES:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r") as f:
            content = f.read()
        if "dotenv" not in content and "os.environ" not in content and "os.getenv" not in content:
            issues.append(f"{filepath}: no env variable loading detected")
    return issues


def check_syntax():
    """Check that all Python files are syntactically valid."""
    issues = []
    for filepath in TARGET_FILES:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            issues.append(f"SYNTAX ERROR in {filepath}: {e}")
    return issues


def main():
    print("=" * 60)
    print("Challenge 2 Validation: Hardcoded Credentials")
    print("=" * 60)

    all_issues = []
    checks = [
        ("No hardcoded credentials", check_no_hardcoded_creds),
        (".env.example exists", check_env_example),
        (".gitignore configured", check_gitignore),
        ("python-dotenv usage", check_dotenv_usage),
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
