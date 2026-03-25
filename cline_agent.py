#!/usr/bin/env python3
"""
Agent Cline-like pour le benchmark.
Boucle agentique avec outils read_file / write_file / list_files,
comme Cline fonctionne dans VS Code.

Usage:
    OPENAI_API_KEY=sk-xxx OPENAI_API_BASE=https://... CLINE_MODEL=openai/Gpt-oss-120b \
        python3 cline_agent.py
"""
import os
import sys
import json
from pathlib import Path
from openai import OpenAI

MAX_ITERATIONS = 10

# ---------------------------------------------------------------------------
# Outils disponibles pour l'agent
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lire le contenu d'un fichier",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin du fichier à lire"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Écrire ou remplacer le contenu d'un fichier",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin du fichier à écrire"},
                    "content": {"type": "string", "description": "Contenu complet du fichier"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lister les fichiers d'un répertoire (récursif)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Répertoire à lister (défaut: .)"}
                },
                "required": []
            }
        }
    },
]


def tool_read_file(path: str) -> str:
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"ERROR: {e}"


def tool_write_file(path: str, content: str) -> str:
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content)
        print(f"  [write] {path}")
        return f"OK: wrote {path}"
    except Exception as e:
        return f"ERROR: {e}"


def tool_list_files(path: str = ".") -> str:
    files = []
    for f in Path(path).rglob("*"):
        if f.is_file() and ".git" not in str(f) and "__pycache__" not in str(f):
            files.append(str(f))
    return "\n".join(sorted(files))


def dispatch_tool(name: str, args: dict) -> str:
    if name == "read_file":
        return tool_read_file(args["path"])
    elif name == "write_file":
        return tool_write_file(args["path"], args["content"])
    elif name == "list_files":
        return tool_list_files(args.get("path", "."))
    return f"ERROR: unknown tool {name}"


def main():
    task_path = Path("TASK.md")
    if not task_path.exists():
        print("Erreur: TASK.md introuvable")
        sys.exit(1)

    model = os.environ.get("CLINE_MODEL", "gpt-4o")
    api_key = os.environ.get("OPENAI_API_KEY")
    api_base = os.environ.get("OPENAI_API_BASE")

    if not api_key:
        print("Erreur: OPENAI_API_KEY non définie")
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=api_base)

    print(f"Agent Cline-like (modèle: {model}, max {MAX_ITERATIONS} itérations)...")

    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un expert Python. Tu as accès à des outils pour lire et écrire des fichiers. "
                "Commence par lire TASK.md et les fichiers source, puis résous la tâche en modifiant "
                "les fichiers nécessaires. Quand tu as terminé, réponds avec 'DONE'."
            )
        },
        {
            "role": "user",
            "content": "Lis TASK.md et résous le challenge décrit dedans. Modifie les fichiers nécessaires."
        }
    ]

    for iteration in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=4096,
        )

        msg = response.choices[0].message
        messages.append(msg)

        # L'agent a terminé
        if response.choices[0].finish_reason == "stop":
            print(f"Agent terminé après {iteration + 1} itération(s).")
            break

        # Exécute les appels d'outils
        if msg.tool_calls:
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = dispatch_tool(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
    else:
        print(f"Attention: limite de {MAX_ITERATIONS} itérations atteinte.")


if __name__ == "__main__":
    main()
