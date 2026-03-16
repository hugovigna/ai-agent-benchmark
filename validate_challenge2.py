"""Validation script for Challenge 2: Hardcoded Credentials.

CE FICHIER : Script de validation automatique du Challenge 2.
COMMENT ÇA MARCHE :
  1. Lit le code source des 4 fichiers cibles
  2. Cherche les patterns de credentials connues (mots de passe, clés API)
  3. Vérifie que .env.example et .gitignore existent et sont corrects
  4. Vérifie que chaque fichier utilise dotenv ou os.getenv()
  5. Vérifie que le Python est syntaxiquement valide (pas de typo)

RÉSULTAT :
  - Affiche PASS/FAIL pour chaque vérification
  - Exit code 0 = tout est bon, 1 = au moins un problème
"""

import ast  # Module standard pour parser du Python sans l'exécuter
import os
import sys
import re


# =============================================================================
# PATTERNS DE CREDENTIALS À CHERCHER
# =============================================================================
# Ce sont les valeurs exactes qui sont hardcodées dans le code original.
# Si on en trouve une dans un fichier source après la correction de l'agent,
# c'est que la credential n'a pas été externalisée → FAIL.
CREDENTIAL_PATTERNS = [
    r"SuperSecret123!",                                # Password PostgreSQL
    r"sk-proj-a8f3k29d4m5n6p7q8r9s0t1u2v3w4x5y6z",   # Clé API
    r"whsec_MIIEvgIBADANBgkqhkiG9w0BAQEFAASC",       # Secret API
    r"AKIAIOSFODNN7EXAMPLE",                           # AWS Access Key ID
    r"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",     # AWS Secret Access Key
    r"hooks\.slack\.com/services/T0123456789",          # URL webhook Slack
    r"gmail_app_password_abcd1234efgh",                # Mot de passe SMTP Gmail
]

# Les 4 fichiers que l'agent doit modifier
TARGET_FILES = [
    "src/db_connector.py",
    "src/api_client.py",
    "src/cloud_storage.py",
    "src/notification.py",
]


# =============================================================================
# CHECK 1 : Vérifier qu'aucune credential n'est restée en dur
# =============================================================================
def check_no_hardcoded_creds():
    """Lit chaque fichier cible et cherche les patterns de credentials.

    C'est le test principal : si on trouve encore "SuperSecret123!" dans
    db_connector.py, l'agent a raté.
    """
    issues = []
    for filepath in TARGET_FILES:
        if not os.path.exists(filepath):
            issues.append(f"MISSING: {filepath}")
            continue
        with open(filepath, "r") as f:
            content = f.read()
        for pattern in CREDENTIAL_PATTERNS:
            if pattern in content:
                # Affiche les 20 premiers caractères du pattern trouvé
                issues.append(f"HARDCODED CRED in {filepath}: found '{pattern[:20]}...'")
    return issues


# =============================================================================
# CHECK 2 : Vérifier que .env.example existe
# =============================================================================
def check_env_example():
    """Vérifie que .env.example existe et contient les noms de variables attendus.

    .env.example est un fichier "modèle" qui montre quelles variables
    d'environnement sont nécessaires, SANS les vraies valeurs.
    Exemple de contenu attendu :
      DB_PASSWORD=
      API_KEY=
      AWS_ACCESS_KEY=
      SLACK_WEBHOOK=
    """
    if not os.path.exists(".env.example"):
        return ["MISSING: .env.example file"]
    with open(".env.example", "r") as f:
        content = f.read()
    # On vérifie que les noms de variables standard sont présents
    expected_vars = ["DB_PASSWORD", "API_KEY", "AWS_ACCESS_KEY", "SLACK_WEBHOOK"]
    missing = [v for v in expected_vars if v not in content]
    if missing:
        return [f".env.example missing variables: {missing}"]
    return []


# =============================================================================
# CHECK 3 : Vérifier que .gitignore exclut .env
# =============================================================================
def check_gitignore():
    """Vérifie que le fichier .env (avec les vraies credentials) ne sera
    pas versionné par Git. C'est CRITIQUE pour la sécurité."""
    if not os.path.exists(".gitignore"):
        return ["MISSING: .gitignore file"]
    with open(".gitignore", "r") as f:
        content = f.read()
    if ".env" not in content:
        return [".gitignore does not exclude .env"]
    return []


# =============================================================================
# CHECK 4 : Vérifier que python-dotenv ou os.getenv est utilisé
# =============================================================================
def check_dotenv_usage():
    """Vérifie que chaque fichier charge ses variables depuis l'environnement.

    Accepte 3 approches valides :
    - from dotenv import load_dotenv (python-dotenv)
    - os.environ["VAR"]
    - os.getenv("VAR")
    """
    issues = []
    for filepath in TARGET_FILES:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r") as f:
            content = f.read()
        if "dotenv" not in content and "os.environ" not in content and "os.getenv" not in content:
            issues.append(f"{filepath}: no env variable loading detected")
    return issues


# =============================================================================
# CHECK 5 : Vérifier que le code Python est syntaxiquement valide
# =============================================================================
def check_syntax():
    """Parse chaque fichier Python avec ast.parse() pour vérifier qu'il n'y a
    pas d'erreur de syntaxe. C'est comme un "compile check" — ça ne l'exécute pas.

    ast = Abstract Syntax Tree = la représentation en arbre du code Python.
    Si ast.parse() lève SyntaxError, le fichier a un problème de syntaxe.
    """
    issues = []
    for filepath in TARGET_FILES:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r") as f:
                ast.parse(f.read())  # Parse sans exécuter
        except SyntaxError as e:
            issues.append(f"SYNTAX ERROR in {filepath}: {e}")
    return issues


# =============================================================================
# ORCHESTRATEUR : Lance tous les checks et affiche le résultat
# =============================================================================
def main():
    print("=" * 60)
    print("Challenge 2 Validation: Hardcoded Credentials")
    print("=" * 60)

    all_issues = []
    # Liste des (nom_du_check, fonction_du_check)
    checks = [
        ("No hardcoded credentials", check_no_hardcoded_creds),
        (".env.example exists", check_env_example),
        (".gitignore configured", check_gitignore),
        ("python-dotenv usage", check_dotenv_usage),
        ("Syntax validity", check_syntax),
    ]

    # Exécute chaque check et affiche PASS ou FAIL
    for name, check_fn in checks:
        issues = check_fn()
        status = "PASS" if not issues else "FAIL"
        print(f"\n[{status}] {name}")
        for issue in issues:
            print(f"  - {issue}")
        all_issues.extend(issues)

    # Résultat global
    print("\n" + "=" * 60)
    if all_issues:
        print(f"RESULT: FAIL ({len(all_issues)} issues found)")
        sys.exit(1)   # Exit code 1 = échec
    else:
        print("RESULT: ALL CHECKS PASSED")
        sys.exit(0)   # Exit code 0 = succès


if __name__ == "__main__":
    main()
