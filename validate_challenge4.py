"""Validation script for Challenge 4: Checkpointing System.

CE FICHIER : Vérifie que l'agent a bien ajouté un système de checkpointing.
STRATÉGIE : On lit tous les fichiers Python dans src/ et on cherche
des mots-clés spécifiques (save, checkpoint, resume, cleanup, force...).
C'est une validation par "pattern matching" sur le code, pas par exécution.
"""

import ast
import os
import sys


# =============================================================================
# CHECK 1 : Un module/classe de checkpointing existe
# =============================================================================
def check_checkpoint_module():
    """Vérifie qu'il existe du code de checkpointing.

    Deux approches acceptées par l'agent :
    a) Créer un fichier séparé src/checkpoint.py (ou src/checkpointer.py)
    b) Ajouter la logique directement dans src/long_pipeline.py

    On cherche d'abord un fichier dédié, sinon on vérifie long_pipeline.py.
    """
    issues = []
    # Cherche des fichiers dont le nom contient "checkpoint"
    checkpoint_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py") and "checkpoint" in f.lower():
                checkpoint_files.append(os.path.join(root, f))

    if not checkpoint_files:
        # Pas de fichier dédié → vérifie si c'est intégré dans long_pipeline.py
        if os.path.exists("src/long_pipeline.py"):
            with open("src/long_pipeline.py", "r") as f:
                content = f.read()
            if "checkpoint" not in content.lower():
                issues.append("No checkpoint module or checkpoint logic found")
        else:
            issues.append("No checkpoint file or long_pipeline.py found")
    return issues


# =============================================================================
# CHECK 2 : Les checkpoints sont sauvegardés
# =============================================================================
def check_save_checkpoint():
    """Vérifie qu'il y a une logique de sauvegarde de checkpoint.

    Cherche :
    - Le mot "save" ET le mot "checkpoint" quelque part dans le code
    - L'utilisation de "json" (pour la sérialisation du context dict)
    """
    issues = []
    py_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    # Concatène tout le code Python dans une seule string pour chercher
    all_content = ""
    for pf in py_files:
        with open(pf, "r") as f:
            all_content += f.read()

    if "save" not in all_content.lower() or "checkpoint" not in all_content.lower():
        issues.append("No save_checkpoint or similar function found")

    # Le context dict doit être sérialisé en JSON pour être persisté sur disque
    if "json" not in all_content:
        issues.append("No JSON serialization detected for checkpoints")

    return issues


# =============================================================================
# CHECK 3 : La logique de reprise existe
# =============================================================================
def check_resume_logic():
    """Vérifie que long_pipeline.py a une logique de reprise.

    Cherche des mots-clés comme "resume", "recover", "restore",
    "load_checkpoint", "last_step", "completed_step", "skip".
    Au moins un de ces mots doit être présent.
    """
    issues = []
    pipeline_path = "src/long_pipeline.py"
    if not os.path.exists(pipeline_path):
        return ["src/long_pipeline.py not found"]

    with open(pipeline_path, "r") as f:
        content = f.read()

    # Liste de mots-clés associés à la logique de reprise
    resume_keywords = ["resume", "recover", "restore", "load_checkpoint", "last_step",
                        "completed_step", "skip"]
    if not any(kw in content.lower() for kw in resume_keywords):
        issues.append("No resume/recovery logic detected in long_pipeline.py")

    return issues


# =============================================================================
# CHECK 4 : Les checkpoints sont nettoyés après succès
# =============================================================================
def check_cleanup():
    """Vérifie que les fichiers de checkpoint sont supprimés après un run réussi.

    Sans nettoyage, les vieux checkpoints s'accumulent sur le disque
    et pourraient interférer avec les prochains runs.
    Cherche des mots-clés comme "clean", "remove", "delete", "unlink".
    """
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


# =============================================================================
# CHECK 5 : Option de force restart
# =============================================================================
def check_force_restart():
    """Vérifie qu'il existe une option pour ignorer les checkpoints.

    Parfois on veut repartir de zéro même s'il y a un checkpoint
    (ex: les données source ont changé, on veut un fresh run).
    L'agent doit ajouter un paramètre force_restart=True ou similaire.
    """
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


# =============================================================================
# CHECK 6b : Les checkpoints sont stockés dans un répertoire dédié
# =============================================================================
def check_checkpoint_directory():
    """Vérifie que les checkpoints sont écrits dans un dossier dédié
    (checkpoints/, .checkpoints/, data/checkpoints/...) et non à la racine."""
    import re
    py_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    all_content = ""
    for pf in py_files:
        with open(pf, "r") as f:
            all_content += f.read()

    dir_patterns = [
        re.compile(r'checkpoints?[/\\]', re.IGNORECASE),
        re.compile(r'checkpoint_dir', re.IGNORECASE),
        re.compile(r'["\']\./checkpoints?["\']'),
    ]
    if not any(p.search(all_content) for p in dir_patterns):
        return ["Checkpoints not stored in a dedicated directory (e.g. checkpoints/)"]
    return []


# =============================================================================
# CHECK 6c : Le checkpoint contient les clés structurelles requises
# =============================================================================
def check_checkpoint_structure():
    """Vérifie que le code écrit un checkpoint avec au minimum les clés
    'step' (ou 'step_number') et 'completed_steps' dans le JSON."""
    py_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    all_content = ""
    for pf in py_files:
        with open(pf, "r") as f:
            all_content += f.read()

    required = ["step", "completed_step"]
    missing = [k for k in required if k not in all_content.lower()]
    if missing:
        return [f"Checkpoint JSON missing structural keys: {missing}"]
    return []


# =============================================================================
# CHECK 6d : Chaque étape est checkpointée individuellement
# =============================================================================
def check_per_step_checkpointing():
    """Vérifie que le checkpoint est appelé à l'intérieur de la boucle
    ou dans le corps de chaque step — pas juste en fin de pipeline."""
    pipeline_path = "src/long_pipeline.py"
    if not os.path.exists(pipeline_path):
        return ["src/long_pipeline.py not found"]

    with open(pipeline_path, "r") as f:
        content = f.read()

    # On cherche "save" ou "checkpoint" dans une boucle ou répété plusieurs fois
    import re
    checkpoint_calls = re.findall(r'(?:save_checkpoint|checkpoint|json\.dump)', content, re.IGNORECASE)
    if len(checkpoint_calls) < 2:
        return ["Checkpoint appears to be called only once (should be called after each step)"]
    return []


# =============================================================================
# CHECK 6 : Syntaxe Python valide
# =============================================================================
def check_syntax():
    """Vérifie que tous les fichiers Python dans src/ sont syntaxiquement valides."""
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


# =============================================================================
# ORCHESTRATEUR DE VALIDATION
# =============================================================================
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
        ("Dedicated checkpoint directory", check_checkpoint_directory),
        ("Checkpoint JSON structure", check_checkpoint_structure),
        ("Per-step checkpointing", check_per_step_checkpointing),
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
