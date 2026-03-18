"""Module de chargement et traitement de fichiers de configuration et données."""

import os
import json
import csv


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_config():
    """Charge la configuration depuis un fichier JSON."""
    config_path = os.path.join(DATA_DIR, "conifg.json")
    with open(config_path, "r") as f:
        return json.load(f)


def load_reference_data():
    """Charge les données de référence depuis un fichier tabulaire."""
    ref_path = os.path.join(DATA_DIR, "reference.csv")
    with open(ref_path, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_mapping_table():
    """Charge la table de mapping depuis un JSON."""
    map_path = os.path.join(DATA_DIR, "mappings.json")
    with open(map_path, "r") as f:
        return json.load(f)


def save_results(results, filename="results"):
    """Sauvegarde les résultats en JSON."""
    output_path = os.path.join(DATA_DIR, filename)
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
