#!/usr/bin/env python3
"""
Validation script for Challenge 6: Retrodocumentation.

Checks that all Python source files follow the documentation template strictly.
"""

import ast
import sys
import os
import re

SRC_DIR = os.path.join(os.getcwd(), "src")
TARGET_FILES = ["data_loader.py", "transformer.py", "exporter.py", "pipeline_runner.py"]

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {label}")
        passed += 1
    else:
        print(f"  ❌ {label}" + (f" — {detail}" if detail else ""))
        failed += 1


def has_type_annotation_in_args(docstring):
    """Check that Args: section has (type) annotations for each param."""
    args_match = re.search(r"Args:\s*\n((?:\s+\w+.*\n)*)", docstring)
    if not args_match:
        return False, "section Args: absente ou vide"
    args_block = args_match.group(1)
    lines = [l.strip() for l in args_block.strip().split("\n") if l.strip()]
    for line in lines:
        if not re.match(r"\w+\s*\(.*\)\s*:", line):
            return False, f"paramètre sans type: '{line.strip()}'"
    return True, ""


def has_returns_with_type(docstring):
    """Check that Returns: section exists and has a type."""
    returns_match = re.search(r"Returns:\s*\n\s+(\S.*)", docstring)
    if not returns_match:
        return False, "section Returns: absente"
    line = returns_match.group(1).strip()
    if not re.match(r"\w.*:", line):
        return False, f"Returns sans type: '{line}'"
    return True, ""


def has_raises_section(docstring):
    """Check if Raises: section is present."""
    return bool(re.search(r"Raises:", docstring))


def function_raises_exceptions(node):
    """Check if a function body contains raise statements."""
    for child in ast.walk(node):
        if isinstance(child, ast.Raise):
            return True
    return False


def validate_file(filepath, filename):
    print(f"\n📄 {filename}")

    # --- Parse ---
    try:
        with open(filepath, "r") as f:
            source = f.read()
        tree = ast.parse(source)
    except SyntaxError as e:
        check("Syntaxe Python valide", False, str(e))
        return

    check("Syntaxe Python valide", True)

    # --- Module docstring ---
    module_doc = ast.get_docstring(tree)
    check("En-tête de module (module docstring)", module_doc is not None)

    # --- Walk all classes and functions ---
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            cls_name = node.name
            doc = ast.get_docstring(node)
            check(f"Docstring classe '{cls_name}'", doc is not None)
            if doc:
                has_attrs = "Attributes:" in doc
                check(f"  Section 'Attributes:' dans '{cls_name}'", has_attrs)

            # Check __init__ specifically
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    init_doc = ast.get_docstring(item)
                    # Only check if __init__ has params beyond self
                    params = [a.arg for a in item.args.args if a.arg != "self"]
                    if params:
                        check(f"  Docstring '{cls_name}.__init__'", init_doc is not None)
                        if init_doc:
                            ok, detail = has_type_annotation_in_args(init_doc)
                            check(f"    Args typés dans '{cls_name}.__init__'", ok, detail)

        if isinstance(node, ast.FunctionDef):
            # Skip if it's a method inside a class - we handle them separately
            # We check all FunctionDef nodes at module level and inside classes
            func_name = node.name

            # Skip dunder methods other than __init__
            if func_name.startswith("__") and func_name.endswith("__") and func_name != "__init__":
                continue

            # __init__ is handled above
            if func_name == "__init__":
                continue

            doc = ast.get_docstring(node)
            check(f"Docstring fonction '{func_name}'", doc is not None)

            if doc:
                # Check Args if function has params (beyond self)
                params = [a.arg for a in node.args.args if a.arg != "self"]
                if params:
                    ok, detail = has_type_annotation_in_args(doc)
                    check(f"  Args typés dans '{func_name}'", ok, detail)

                # Check Returns
                ok, detail = has_returns_with_type(doc)
                check(f"  Returns typé dans '{func_name}'", ok, detail)

                # Check Raises if function raises exceptions
                if function_raises_exceptions(node):
                    check(f"  Section 'Raises:' dans '{func_name}'", has_raises_section(doc))


def main():
    global passed, failed

    print("=" * 60)
    print("  Challenge 6 — Validation Rétrodocumentation")
    print("=" * 60)

    # Check all target files exist
    for filename in TARGET_FILES:
        filepath = os.path.join(SRC_DIR, filename)
        if not os.path.exists(filepath):
            print(f"\n❌ Fichier manquant: {filename}")
            failed += 1
            continue
        validate_file(filepath, filename)

    # --- Summary ---
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"  Résultat: {passed}/{total} checks passés")
    if failed == 0:
        print("  🎉 CHALLENGE 6 RÉUSSI !")
    else:
        print(f"  ⚠️  {failed} check(s) échoué(s)")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
