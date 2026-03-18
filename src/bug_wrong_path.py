"""
Bug 3 : Fonctions qui pointent vers des fichiers mal écrits

Ce module charge et traite des fichiers de configuration et de données.
Plusieurs chemins de fichiers sont mal construits (typos, mauvaise extension,
mauvais séparateur de chemin).
"""

import os
import json
import csv


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_config():
    """Charge la configuration depuis un fichier JSON.

    BUG: le nom du fichier a une typo ('conifg' au lieu de 'config').
    """
    config_path = os.path.join(DATA_DIR, "conifg.json")  # BUG: typo 'conifg'
    with open(config_path, "r") as f:
        return json.load(f)


def load_reference_data():
    """Charge les données de référence depuis un CSV.

    BUG: mauvaise extension (.csv au lieu de .tsv, le fichier réel est un TSV).
    """
    ref_path = os.path.join(DATA_DIR, "reference.csv")  # BUG: le fichier est .tsv
    with open(ref_path, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_mapping_table():
    """Charge la table de mapping depuis un JSON.

    BUG: utilise un double slash dans le chemin qui casse sous certains OS,
    et le nom de fichier est 'mappings' (pluriel) au lieu de 'mapping'.
    """
    map_path = os.path.join(DATA_DIR, "mappings.json")  # BUG: 'mappings' au lieu de 'mapping'
    with open(map_path, "r") as f:
        return json.load(f)


def save_results(results, filename="results"):
    """Sauvegarde les résultats en JSON.

    BUG: oubli de l'extension dans le chemin de sortie.
    """
    output_path = os.path.join(DATA_DIR, filename)  # BUG: manque '.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    return output_path


def process_files():
    """Point d'entrée — charge les fichiers et produit un résultat combiné."""
    config = load_config()
    reference = load_reference_data()
    mapping = load_mapping_table()

    combined = {
        "config": config,
        "reference_count": len(reference),
        "mapping_keys": list(mapping.keys()),
    }

    output_path = save_results(combined)
    return {"status": "ok", "output": output_path, "data": combined}
