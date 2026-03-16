"""Validation script for Challenge 3: Pipeline Refactoring.

CE FICHIER : Vérifie automatiquement que l'agent a bien refactoré le pipeline.
STRATÉGIE DE VALIDATION :
  On utilise l'AST (Abstract Syntax Tree) de Python pour analyser le code
  sans l'exécuter. On cherche si les bonnes fonctions existent dans les bons
  fichiers, si le logging est présent, et si l'orchestrateur utilise les 3 modules.
"""

import ast       # Pour parser du Python et extraire les noms de fonctions
import os
import sys
import importlib.util


# Les 4 fichiers que l'agent doit créer
EXPECTED_MODULES = [
    "src/pipeline/__init__.py",    # Orchestrateur
    "src/pipeline/extract.py",     # Extraction des données
    "src/pipeline/transform.py",   # Transformation des données
    "src/pipeline/load.py",        # Chargement / écriture des résultats
]


# =============================================================================
# CHECK 1 : Structure du package
# =============================================================================
def check_package_structure():
    """Vérifie que :
    - src/pipeline.py N'EXISTE PLUS (remplacé par le package)
    - src/pipeline/ existe avec les 4 fichiers attendus

    En Python, un "package" = un dossier avec un __init__.py.
    Quand on fait "from src.pipeline import ...", Python cherche
    soit src/pipeline.py soit src/pipeline/__init__.py.
    Les deux ne peuvent pas coexister.
    """
    issues = []
    if os.path.exists("src/pipeline.py"):
        issues.append("src/pipeline.py still exists (should be replaced by src/pipeline/)")
    for module_path in EXPECTED_MODULES:
        if not os.path.exists(module_path):
            issues.append(f"MISSING: {module_path}")
    return issues


# =============================================================================
# CHECK 2 : Module extract.py
# =============================================================================
def check_extract_module():
    """Vérifie que extract.py contient des fonctions de découverte et parsing.

    On parse le fichier avec ast et on extrait les noms de fonctions.
    On cherche des noms comme "discover_files", "parse_csv", "read_sources", etc.
    La vérification est souple : on cherche des mots-clés dans les noms.
    """
    path = "src/pipeline/extract.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    # ast.walk parcourt tout l'arbre et FunctionDef = définition de fonction
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    issues = []
    # Cherche une fonction de découverte de fichiers
    if not any("discover" in fn or "source" in fn or "find" in fn for fn in func_names):
        issues.append("extract.py: no file discovery function found")
    # Cherche une fonction de parsing CSV/JSON
    if not any("csv" in fn.lower() or "parse" in fn.lower() or "read" in fn.lower() for fn in func_names):
        issues.append("extract.py: no CSV/JSON parsing function found")
    return issues


# =============================================================================
# CHECK 3 : Module transform.py
# =============================================================================
def check_transform_module():
    """Vérifie que transform.py a les 4 types de transformation attendus :
    - dedup (déduplication)
    - clean (nettoyage)
    - valid (validation)
    - enrich (enrichissement)

    Cherche ces mots-clés dans les noms de fonctions.
    """
    path = "src/pipeline/transform.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    issues = []
    # On s'attend à une fonction par concept de transformation
    expected_concepts = ["dedup", "clean", "valid", "enrich"]
    for concept in expected_concepts:
        if not any(concept in fn.lower() for fn in func_names):
            issues.append(f"transform.py: no function related to '{concept}'")
    return issues


# =============================================================================
# CHECK 4 : Module load.py
# =============================================================================
def check_load_module():
    """Vérifie que load.py a des fonctions d'écriture de fichiers.

    Cherche des noms comme "write_output", "save_results", "load_data", etc.
    """
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


# =============================================================================
# CHECK 5 : Logging présent dans tous les modules
# =============================================================================
def check_logging_present():
    """Vérifie que chaque module utilise le logging Python.

    Un bon pipeline doit logger ce qu'il fait pour le debugging
    et le monitoring en production.
    """
    issues = []
    for module_path in EXPECTED_MODULES:
        if not os.path.exists(module_path):
            continue
        with open(module_path, "r") as f:
            content = f.read()
        if "logging" not in content and "logger" not in content:
            issues.append(f"{module_path}: no logging detected")
    return issues


# =============================================================================
# CHECK 6 : L'orchestrateur utilise les 3 modules
# =============================================================================
def check_orchestrator():
    """Vérifie que __init__.py importe et utilise extract, transform et load.

    L'orchestrateur est le point d'entrée qui appelle les 3 modules
    dans le bon ordre. Si il n'importe pas un module, la refactorisation
    est incomplète.
    """
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


# =============================================================================
# CHECK 7 : Validité syntaxique
# =============================================================================
def check_syntax():
    """Vérifie que tous les fichiers Python sont syntaxiquement valides."""
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


# =============================================================================
# ORCHESTRATEUR DE VALIDATION
# =============================================================================
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
