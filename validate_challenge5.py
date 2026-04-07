"""Validation script for Challenge 5: Data Quality Module.

CE FICHIER : Le validateur le plus complexe du benchmark.
Vérifie que l'agent a créé un module complet de data quality avec :
  - Un profiler (calculs statistiques)
  - Un générateur de rapport JSON
  - Des quality gates (seuils bloquants)
  - Un fichier de configuration externe
  - De la détection d'anomalies

STRATÉGIE DE VALIDATION :
On combine la vérification de structure (fichiers existent ?),
l'analyse AST (bonnes fonctions ?), et la recherche de mots-clés
(concepts statistiques présents dans le code ?).
"""

import ast
import json
import os
import sys


# Les 4 fichiers Python attendus dans le module data_quality
EXPECTED_FILES = [
    "src/data_quality/__init__.py",      # Point d'entrée du package
    "src/data_quality/profiler.py",      # Calculs de profiling
    "src/data_quality/report.py",        # Génération du rapport JSON
    "src/data_quality/quality_gate.py",  # Vérification des seuils
]


# =============================================================================
# CHECK 1 : Structure du module
# =============================================================================
def check_module_structure():
    """Vérifie que le package src/data_quality/ existe avec les 4 fichiers.

    Note : on ne vérifie pas config.py ici car c'est optionnel
    (la config peut être chargée directement dans quality_gate.py).
    """
    issues = []
    for filepath in EXPECTED_FILES:
        if not os.path.exists(filepath):
            issues.append(f"MISSING: {filepath}")
    return issues


# =============================================================================
# CHECK 2 : Le profiler a les bonnes fonctionnalités
# =============================================================================
def check_profiler():
    """Vérifie que profiler.py contient les concepts de profiling requis.

    On cherche des mots-clés dans le code :
    - "null" → détection des valeurs manquantes
    - "unique" → comptage de la cardinalité
    - "distribution" → calcul de la distribution statistique

    On cherche aussi des fonctions statistiques (mean, median, std, etc.)
    """
    path = "src/data_quality/profiler.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()

    issues = []
    # Concepts de profiling attendus
    required_concepts = {
        "null": "null/missing value detection",         # Valeurs manquantes
        "unique": "cardinality/unique value counting",  # Valeurs uniques
        "distribution": "distribution statistics (min/max/mean/std)",  # Stats
    }
    content_lower = content.lower()
    for keyword, description in required_concepts.items():
        if keyword not in content_lower and keyword.replace("_", " ") not in content_lower:
            issues.append(f"profiler.py: missing {description} (keyword: '{keyword}')")

    # Fonctions statistiques (au moins une doit être présente)
    stat_keywords = ["mean", "median", "std", "min", "max", "average"]
    if not any(kw in content_lower for kw in stat_keywords):
        issues.append("profiler.py: no statistical calculations detected")

    return issues


# =============================================================================
# CHECK 3 : Le rapport JSON est généré
# =============================================================================
def check_report_generation():
    """Vérifie que report.py :
    1. Utilise le module json (pour générer le rapport)
    2. A une fonction dont le nom contient "report" ou "generate"
    """
    path = "src/data_quality/report.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()

    issues = []
    if "json" not in content:
        issues.append("report.py: no JSON handling detected")

    # Extrait les noms de fonctions via AST
    tree = ast.parse(content)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    if not any("report" in fn.lower() or "generate" in fn.lower() for fn in func_names):
        issues.append("report.py: no report generation function found")

    return issues


# =============================================================================
# CHECK 4 : Les quality gates bloquent le pipeline
# =============================================================================
def check_quality_gates():
    """Vérifie que quality_gate.py :
    1. A une logique de vérification de seuils (threshold, limit, gate...)
    2. Peut bloquer le pipeline (raise, error, fail...)

    Un quality gate DOIT pouvoir stopper le pipeline — sinon c'est juste
    un rapport informatif, pas un garde-fou.
    """
    path = "src/data_quality/quality_gate.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]
    with open(path, "r") as f:
        content = f.read()

    issues = []
    content_lower = content.lower()

    # Vérification de seuils
    threshold_keywords = ["threshold", "limit", "max_null", "completeness", "gate"]
    if not any(kw in content_lower for kw in threshold_keywords):
        issues.append("quality_gate.py: no threshold checking detected")

    # Mécanisme de blocage (raise Exception, sys.exit, return error, etc.)
    block_keywords = ["raise", "error", "block", "fail", "reject", "exception"]
    if not any(kw in content_lower for kw in block_keywords):
        issues.append("quality_gate.py: no pipeline blocking mechanism detected")

    return issues


# =============================================================================
# CHECK 5 : Fichier de configuration des seuils
# =============================================================================
def check_config_file():
    """Vérifie qu'un fichier de config des seuils existe dans config/.

    Accepte JSON ou YAML, avec plusieurs noms possibles.
    Si c'est du JSON, on vérifie qu'il est parseable.
    """
    config_paths = [
        "config/quality_thresholds.json",
        "config/quality_thresholds.yaml",
        "config/quality_thresholds.yml",
        "config/quality_config.json",
        "config/quality_config.yaml",
    ]
    for path in config_paths:
        if os.path.exists(path):
            if path.endswith(".json"):
                try:
                    with open(path, "r") as f:
                        json.load(f)  # Vérifie que le JSON est valide
                    return []  # OK
                except json.JSONDecodeError as e:
                    return [f"Config file {path} is not valid JSON: {e}"]
            return []  # YAML trouvé, on fait confiance

    return ["No quality thresholds config file found in config/"]


# =============================================================================
# CHECK 6 : Détection d'anomalies
# =============================================================================
def check_anomaly_detection():
    """Vérifie que le module contient une logique de détection d'anomalies.

    Une anomalie = une valeur statistiquement anormale.
    Méthodes courantes :
    - Z-score : valeur à >3 écarts-types de la moyenne
    - IQR : valeur hors [Q1 - 1.5*IQR, Q3 + 1.5*IQR]

    On cherche des mots-clés liés à ces concepts dans tout le module.
    """
    issues = []
    all_content = ""
    for root, dirs, files in os.walk("src/data_quality"):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r") as fh:
                    all_content += fh.read()

    content_lower = all_content.lower()
    # Mots-clés associés à la détection d'anomalies
    anomaly_keywords = ["anomal", "outlier", "zscore", "z_score", "std", "deviation",
                        "iqr", "interquartile"]
    if not any(kw in content_lower for kw in anomaly_keywords):
        issues.append("No anomaly/outlier detection logic found")

    return issues


# =============================================================================
# CHECK 7b : Le fichier de config contient les 4 seuils requis
# =============================================================================
def check_config_has_required_thresholds():
    """Vérifie que le fichier de config contient bien les 4 seuils définis
    dans le TASK.md — pas juste un fichier JSON vide ou générique."""
    import re
    config_paths = [
        "config/quality_thresholds.json",
        "config/quality_thresholds.yaml",
        "config/quality_thresholds.yml",
        "config/quality_config.json",
        "config/quality_config.yaml",
    ]
    config_path = next((p for p in config_paths if os.path.exists(p)), None)
    if not config_path:
        return ["No config file found — cannot check thresholds"]

    with open(config_path, "r") as f:
        content = f.read().lower()

    required_keys = ["max_null_percentage", "min_completeness",
                     "max_duplicate_percentage", "anomaly_threshold"]
    missing = [k for k in required_keys if k not in content]
    if missing:
        return [f"Config missing required threshold keys: {missing}"]
    return []


# =============================================================================
# CHECK 7c : Le rapport JSON a la structure minimale attendue
# =============================================================================
def check_report_json_structure():
    """Vérifie que le rapport JSON généré contient les clés obligatoires :
    timestamp, total_records, columns, quality_score."""
    path = "src/data_quality/report.py"
    if not os.path.exists(path):
        return [f"MISSING: {path}"]

    with open(path, "r") as f:
        content = f.read().lower()

    required_keys = ["timestamp", "total_records", "quality_score", "columns"]
    missing = [k for k in required_keys if k not in content]
    if missing:
        return [f"report.py: JSON structure missing keys: {missing}"]
    return []


# =============================================================================
# CHECK 7d : Détection d'anomalies à 3-sigma (pas juste un mot-clé vague)
# =============================================================================
def check_three_sigma():
    """Vérifie que la détection d'anomalies utilise bien le seuil à 3 écarts-types
    (z-score > 3) comme défini dans les specs, et pas juste un mot-clé générique."""
    import re
    all_content = ""
    for root, dirs, files in os.walk("src/data_quality"):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r") as fh:
                    all_content += fh.read()

    # Cherche la valeur 3 associée à std/sigma/z-score
    sigma_patterns = [
        re.compile(r'\b3\b.*(?:std|sigma|z.?score)', re.IGNORECASE),
        re.compile(r'(?:std|sigma|z.?score).*\b3\b', re.IGNORECASE),
        re.compile(r'anomaly_threshold.*[=:]\s*3', re.IGNORECASE),
    ]
    if not any(p.search(all_content) for p in sigma_patterns):
        return ["Anomaly detection does not explicitly use 3-sigma threshold"]
    return []


# =============================================================================
# CHECK 7 : Syntaxe Python valide
# =============================================================================
def check_syntax():
    """Vérifie que tous les fichiers Python du module sont syntaxiquement valides."""
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


# =============================================================================
# ORCHESTRATEUR DE VALIDATION
# =============================================================================
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
        ("Config has required thresholds", check_config_has_required_thresholds),
        ("Report JSON structure", check_report_json_structure),
        ("Anomaly detection", check_anomaly_detection),
        ("3-sigma threshold", check_three_sigma),
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
