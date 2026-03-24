#!/usr/bin/env python3
"""
Agent GitHub Copilot pour le benchmark.
Lit TASK.md, lit les fichiers source, appelle l'API Copilot et applique les modifications.
"""
import os
import re
import sys
import subprocess
from pathlib import Path

from openai import OpenAI


def get_github_token():
    result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
    token = result.stdout.strip()
    if not token:
        print("Erreur: impossible de récupérer le token GitHub (gh auth token)")
        sys.exit(1)
    return token


def get_source_files():
    files = {}
    for f in Path('.').rglob('*.py'):
        if '.git' not in str(f):
            try:
                files[str(f)] = f.read_text()
            except Exception:
                pass
    return files


def apply_changes(output):
    pattern = r'=== FILE: (.+?) ===\n(.*?)=== END FILE ==='
    matches = re.findall(pattern, output, re.DOTALL)
    if not matches:
        print("Aucune modification trouvée dans la réponse.")
        print("Réponse brute:", output[:500])
        sys.exit(1)
    for filepath, content in matches:
        filepath = filepath.strip()
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(content.strip() + '\n')
        print(f"  Modifié: {filepath}")
    return len(matches)


def main():
    task_path = Path('TASK.md')
    if not task_path.exists():
        print("Erreur: TASK.md introuvable")
        sys.exit(1)
    task = task_path.read_text()

    source_files = get_source_files()
    files_str = '\n\n'.join(f"=== {p} ===\n{c}" for p, c in source_files.items())

    model = os.environ.get('COPILOT_MODEL', 'gpt-4o')
    token = get_github_token()

    client = OpenAI(
        base_url="https://api.githubcopilot.com",
        api_key=token,
    )

    print(f"Appel GitHub Copilot (modèle: {model})...")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un expert Python. On te donne une tâche et des fichiers source. "
                    "Résous la tâche en modifiant les fichiers nécessaires.\n"
                    "Réponds UNIQUEMENT avec les fichiers modifiés dans ce format exact :\n"
                    "=== FILE: chemin/du/fichier.py ===\n"
                    "<contenu complet du fichier>\n"
                    "=== END FILE ==="
                )
            },
            {
                "role": "user",
                "content": f"Tâche:\n{task}\n\nFichiers actuels:\n{files_str}\n\nRésous la tâche."
            }
        ],
        max_tokens=4096,
    )

    output = response.choices[0].message.content
    print("Réponse reçue, application des modifications...")
    n = apply_changes(output)
    print(f"Terminé: {n} fichier(s) modifié(s)")


if __name__ == '__main__':
    main()
