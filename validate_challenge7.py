#!/usr/bin/env python3
"""
Validation script for Challenge 7: Codebase Mapping.

Checks that MAPPING.md exists and contains all required modules, classes,
functions, dependencies, and entry points.
"""

import ast
import sys
import os
import re

MAPPING_FILE = os.path.join(os.path.dirname(__file__), "MAPPING.md")

# --- Ground truth: what the mapping must contain ---

EXPECTED_MODULES = [
    "config/settings.py",
    "src/models.py",
    "src/ingestion.py",
    "src/transform.py",
    "src/export.py",
    "src/orchestrator.py",
]

EXPECTED_CLASSES = [
    "Record",
    "BatchResult",
    "PipelineState",
    "IngestionPipeline",
    "TransformChain",
    "ReportGenerator",
    "PipelineOrchestrator",
    "PipelineConfig",
]

EXPECTED_FUNCTIONS = [
    "read_csv_source",
    "read_json_source",
    "parse_records",
    "clean_dataframe",
    "normalize_columns",
    "apply_transformations",
    "add_features",
    "write_csv",
    "write_json",
    "write_parquet",
    "run_pipeline",
]

# Internal import edges (module_from -> module_to)
EXPECTED_DEPENDENCIES = [
    ("src/ingestion.py", "src/models.py"),
    ("src/ingestion.py", "config/settings.py"),
    ("src/transform.py", "src/models.py"),
    ("src/export.py", "config/settings.py"),
    ("src/orchestrator.py", "src/ingestion.py"),
    ("src/orchestrator.py", "src/transform.py"),
    ("src/orchestrator.py", "src/export.py"),
    ("src/orchestrator.py", "src/models.py"),
    ("src/orchestrator.py", "config/settings.py"),
]

ENTRY_POINTS = ["PipelineOrchestrator", "run_pipeline"]

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


def normalize(text):
    """Normalize text for fuzzy matching: lowercase, remove extra spaces."""
    return re.sub(r'\s+', ' ', text.lower().strip())


def content_contains(content_lower, term):
    """Check if a term appears in the content (case-insensitive, flexible matching)."""
    term_lower = term.lower()
    # Try exact match
    if term_lower in content_lower:
        return True
    # Try without path prefix (e.g. "settings.py" for "config/settings.py")
    basename = os.path.basename(term_lower)
    if basename in content_lower:
        return True
    # Try with dots instead of slashes (e.g. "config.settings")
    dotted = term_lower.replace("/", ".").replace(".py", "")
    if dotted in content_lower:
        return True
    return False


def main():
    global passed, failed

    print("=" * 60)
    print("  Challenge 7 — Validation Mapping")
    print("=" * 60)

    # --- Check file exists ---
    check("MAPPING.md existe", os.path.exists(MAPPING_FILE))
    if not os.path.exists(MAPPING_FILE):
        print("\n❌ Impossible de continuer sans MAPPING.md")
        sys.exit(1)

    with open(MAPPING_FILE, "r") as f:
        content = f.read()
    content_lower = content.lower()

    # --- Check required sections ---
    print("\n📋 Sections obligatoires")
    sections = ["## Modules", "## Classes", "## Fonctions", "## Dépendances", "## Point"]
    section_labels = ["Modules", "Classes", "Fonctions", "Dépendances", "Point d'entrée"]
    for section, label in zip(sections, section_labels):
        # Flexible: accept variations like "## Modules", "## 1. Modules", "## Fonctions standalone"
        pattern = r"##\s+(?:\d+\.\s*)?" + re.escape(label.split()[0])
        found = bool(re.search(pattern, content, re.IGNORECASE))
        check(f"Section '{label}'", found)

    # --- Check all modules listed ---
    print("\n📦 Modules")
    for mod in EXPECTED_MODULES:
        check(f"Module '{mod}'", content_contains(content_lower, mod))

    # --- Check all classes listed ---
    print("\n🏗️  Classes")
    for cls in EXPECTED_CLASSES:
        check(f"Classe '{cls}'", cls.lower() in content_lower or cls in content)

    # --- Check all functions listed ---
    print("\n⚙️  Fonctions standalone")
    for func in EXPECTED_FUNCTIONS:
        check(f"Fonction '{func}'", func.lower() in content_lower or func in content)

    # --- Check methods are documented for key classes ---
    print("\n🔍 Méthodes des classes clés")
    EXPECTED_METHODS = {
        "PipelineOrchestrator": ["run", "setup"],
        "IngestionPipeline": ["ingest", "load"],
        "PipelineConfig": ["validate", "from_dict"],
    }
    for cls_name, methods in EXPECTED_METHODS.items():
        for method in methods:
            check(
                f"{cls_name}.{method}()",
                method.lower() in content_lower,
                f"méthode '{method}' de {cls_name} non documentée"
            )

    # --- Check dependencies ---
    print("\n🔗 Dépendances internes")
    dep_found = 0
    for src_mod, dst_mod in EXPECTED_DEPENDENCIES:
        # Check if both modules appear near each other or in a dependency line
        src_base = os.path.basename(src_mod).replace(".py", "")
        dst_base = os.path.basename(dst_mod).replace(".py", "")
        # Look for patterns like "ingestion -> models", "src/ingestion.py -> src/models.py", etc.
        found = False
        # Pattern 1: arrow notation
        if re.search(rf"{src_base}.*(?:->|→|=>|imports?|dépend).*{dst_base}", content_lower):
            found = True
        # Pattern 2: reverse mention (dst imported by src)
        if re.search(rf"{dst_base}.*(?:importé|used|imported).*{src_base}", content_lower):
            found = True
        # Pattern 3: both appear in same line/row
        lines = content.split("\n")
        for line in lines:
            ll = line.lower()
            if src_base in ll and dst_base in ll:
                found = True
                break
        if found:
            dep_found += 1

    check(
        f"Dépendances documentées ({dep_found}/{len(EXPECTED_DEPENDENCIES)})",
        dep_found >= len(EXPECTED_DEPENDENCIES) * 0.9,
        f"au moins {int(len(EXPECTED_DEPENDENCIES) * 0.9)} attendues sur {len(EXPECTED_DEPENDENCIES)}"
    )

    # --- Check entry point ---
    print("\n🚀 Point d'entrée")
    entry_found = any(ep.lower() in content_lower or ep in content for ep in ENTRY_POINTS)
    check("Point d'entrée identifié", entry_found)

    # --- Summary ---
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"  Résultat: {passed}/{total} checks passés")
    if failed == 0:
        print("  🎉 CHALLENGE 7 RÉUSSI !")
    else:
        print(f"  ⚠️  {failed} check(s) échoué(s)")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
