"""Main data pipeline - processes raw data end to end.

CE FICHIER : Le pipeline monolithique — c'est le coeur du Challenge 3.
PROBLÈME : Tout le traitement (271 lignes) est dans UNE SEULE FONCTION.
C'est un "God Function" anti-pattern : impossible à tester unitairement,
difficile à maintenir, et si on veut changer juste l'extraction, on doit
toucher tout le fichier.

CE QUE L'AGENT DOIT FAIRE :
Découper cette fonction en 3 modules séparés :
  - extract.py  : Étapes 1-3 (découverte fichiers + parsing CSV + parsing JSON)
  - transform.py: Étapes 4-8 (merge + dedup + clean + validate + enrich)
  - load.py     : Étapes 9-10 (agrégation + écriture fichiers)
Avec un orchestrateur dans __init__.py qui appelle le tout dans l'ordre.

ARCHITECTURE ETL :
Le pipeline suit le pattern classique ETL (Extract-Transform-Load) :
  Extract  = lire les données brutes depuis les fichiers source
  Transform = nettoyer, dédupliquer, valider, enrichir les données
  Load     = écrire les résultats dans les fichiers de sortie
"""

import os
import csv
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


def run_pipeline(input_dir, output_dir):
    """Exécute le pipeline complet de bout en bout.

    Paramètres :
      input_dir  : dossier contenant les fichiers source (CSV + JSON)
      output_dir : dossier où écrire les résultats

    Retourne :
      Un dictionnaire "manifest" résumant le run (nb records, durée, etc.)
    """
    start_time = time.time()
    logger.info("Pipeline started at %s", datetime.now().isoformat())

    # ============================================================
    # STEP 1: Discover source files (EXTRACT)
    # ============================================================
    # Parcourt récursivement input_dir pour trouver tous les .csv et .json
    # os.walk() retourne (dossier_courant, sous_dossiers, fichiers)
    source_files = []
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.endswith(".csv") or f.endswith(".json"):
                full_path = os.path.join(root, f)
                file_size = os.path.getsize(full_path)  # Taille en octets
                source_files.append({
                    "path": full_path,
                    "name": f,
                    "size": file_size,
                    "type": f.split(".")[-1],  # Extension du fichier
                })
    logger.info("Discovered %d source files", len(source_files))
    if not source_files:
        logger.warning("No source files found in %s", input_dir)
        return {"status": "NO_DATA", "records": 0}

    # ============================================================
    # STEP 2: Read and parse CSV files (EXTRACT)
    # ============================================================
    # csv.DictReader lit chaque ligne comme un dictionnaire {colonne: valeur}
    # On ajoute des métadonnées (_source_file, _ingested_at) à chaque record
    csv_records = []
    for file_info in source_files:
        if file_info["type"] != "csv":
            continue
        try:
            with open(file_info["path"], "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    row["_source_file"] = file_info["name"]       # Traçabilité : d'où vient ce record
                    row["_ingested_at"] = datetime.now().isoformat()  # Quand on l'a lu
                    csv_records.append(row)
        except Exception as e:
            logger.error("Failed to read CSV %s: %s", file_info["path"], e)
    logger.info("Parsed %d records from CSV files", len(csv_records))

    # ============================================================
    # STEP 3: Read and parse JSON files (EXTRACT)
    # ============================================================
    # Gère deux cas : un fichier JSON peut contenir une liste [...] ou un objet {...}
    json_records = []
    for file_info in source_files:
        if file_info["type"] != "json":
            continue
        try:
            with open(file_info["path"], "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    # Si c'est une liste, chaque élément est un record
                    for record in data:
                        record["_source_file"] = file_info["name"]
                        record["_ingested_at"] = datetime.now().isoformat()
                        json_records.append(record)
                elif isinstance(data, dict):
                    # Si c'est un objet unique, c'est un seul record
                    data["_source_file"] = file_info["name"]
                    data["_ingested_at"] = datetime.now().isoformat()
                    json_records.append(data)
        except Exception as e:
            logger.error("Failed to read JSON %s: %s", file_info["path"], e)
    logger.info("Parsed %d records from JSON files", len(json_records))

    # ============================================================
    # STEP 4: Merge all records (TRANSFORM)
    # ============================================================
    # Simple concaténation des records CSV et JSON dans une seule liste
    all_records = csv_records + json_records
    logger.info("Total raw records: %d", len(all_records))

    # ============================================================
    # STEP 5: Deduplicate records (TRANSFORM)
    # ============================================================
    # Stratégie : calculer un hash MD5 de chaque record (sérialisé en JSON)
    # Si deux records ont le même hash, c'est un doublon → on le skip
    # Note : MD5 n'est PAS sécurisé pour la crypto, mais OK pour la dédup
    seen_hashes = set()       # Ensemble des hashes déjà vus
    unique_records = []       # Records uniques conservés
    duplicate_count = 0
    for record in all_records:
        # sort_keys=True garantit le même hash pour {"a":1,"b":2} et {"b":2,"a":1}
        record_str = json.dumps(record, sort_keys=True, default=str)
        record_hash = hashlib.md5(record_str.encode()).hexdigest()
        if record_hash not in seen_hashes:
            seen_hashes.add(record_hash)
            record["_hash"] = record_hash  # On stocke le hash pour traçabilité
            unique_records.append(record)
        else:
            duplicate_count += 1
    logger.info("Removed %d duplicates, %d unique records remain",
                duplicate_count, len(unique_records))

    # ============================================================
    # STEP 6: Clean and normalize fields (TRANSFORM)
    # ============================================================
    # Pour chaque record, on normalise :
    # - Les clés : minuscules, espaces→underscores (ex: "First Name"→"first_name")
    # - Les valeurs string : trim, conversion des "null"/"N/A"/""→None
    # - Les valeurs numériques en string : conversion en int/float
    cleaned_records = []
    for record in unique_records:
        cleaned = {}
        for key, value in record.items():
            # Normalisation de la clé
            clean_key = key.strip().lower().replace(" ", "_").replace("-", "_")
            if isinstance(value, str):
                value = value.strip()
                # Conversion des représentations textuelles de "vide" en None
                if value.lower() in ("null", "none", "n/a", "na", ""):
                    value = None
                # Tentative de conversion des strings numériques en nombres
                elif value.replace(".", "").replace("-", "").isdigit():
                    try:
                        value = float(value) if "." in value else int(value)
                    except ValueError:
                        pass  # Si la conversion échoue, on garde le string
            cleaned[clean_key] = value
        cleaned_records.append(cleaned)
    logger.info("Cleaned %d records", len(cleaned_records))

    # ============================================================
    # STEP 7: Validate required fields (TRANSFORM)
    # ============================================================
    # Chaque record DOIT avoir les champs id, timestamp et value.
    # S'il en manque un, le record est marqué invalide et mis de côté.
    required_fields = ["id", "timestamp", "value"]
    valid_records = []
    invalid_records = []
    for record in cleaned_records:
        # Vérifie que chaque champ requis existe ET n'est pas None
        missing = [f for f in required_fields if f not in record or record[f] is None]
        if missing:
            record["_validation_errors"] = missing  # Note quels champs manquent
            invalid_records.append(record)
        else:
            valid_records.append(record)
    logger.info("Validation: %d valid, %d invalid records",
                len(valid_records), len(invalid_records))

    # ============================================================
    # STEP 8: Enrich records with computed fields (TRANSFORM)
    # ============================================================
    # Ajoute des champs calculés à partir des données existantes :
    # - _date, _hour, _day_of_week, _is_weekend → depuis le timestamp
    # - _value_bucket → catégorise la valeur (low/medium/high/very_high)
    enriched_records = []
    for record in valid_records:
        # --- Enrichissement temporel ---
        try:
            if "timestamp" in record and record["timestamp"]:
                ts = str(record["timestamp"])
                if ts.isdigit():
                    # Timestamp Unix (ex: 1705312200)
                    dt = datetime.fromtimestamp(int(ts))
                else:
                    # Format ISO (ex: "2024-01-15T10:30:00")
                    dt = datetime.fromisoformat(ts)
                record["_date"] = dt.strftime("%Y-%m-%d")       # "2024-01-15"
                record["_hour"] = dt.hour                        # 10
                record["_day_of_week"] = dt.strftime("%A")      # "Monday"
                record["_is_weekend"] = dt.weekday() >= 5       # True/False
        except Exception as e:
            logger.warning("Failed to parse timestamp for record %s: %s",
                           record.get("id"), e)
            record["_date"] = None
            record["_hour"] = None
            record["_day_of_week"] = None
            record["_is_weekend"] = None

        # --- Enrichissement par bucket de valeur ---
        if "value" in record and record["value"] is not None:
            try:
                val = float(record["value"])
                record["_value_bucket"] = (
                    "low" if val < 10           # < 10 = "low"
                    else "medium" if val < 100  # 10-99 = "medium"
                    else "high" if val < 1000   # 100-999 = "high"
                    else "very_high"            # >= 1000 = "very_high"
                )
            except (ValueError, TypeError):
                record["_value_bucket"] = "unknown"

        record["_processed_at"] = datetime.now().isoformat()
        enriched_records.append(record)
    logger.info("Enriched %d records", len(enriched_records))

    # ============================================================
    # STEP 9: Aggregate statistics (LOAD)
    # ============================================================
    # Calcule des statistiques globales sur le dataset traité :
    # - Ventilation par date, par bucket, par source
    # - Statistiques numériques (somme, min, max, moyenne)
    # defaultdict(int) → si la clé n'existe pas, elle vaut 0 par défaut
    stats = {
        "total_records": len(enriched_records),
        "by_date": defaultdict(int),      # Compteur par date
        "by_bucket": defaultdict(int),    # Compteur par bucket de valeur
        "by_source": defaultdict(int),    # Compteur par fichier source
        "value_sum": 0,
        "value_count": 0,
        "value_min": float("inf"),        # +infini (tout sera plus petit)
        "value_max": float("-inf"),       # -infini (tout sera plus grand)
    }
    for record in enriched_records:
        date = record.get("_date", "unknown")
        stats["by_date"][date] += 1
        bucket = record.get("_value_bucket", "unknown")
        stats["by_bucket"][bucket] += 1
        source = record.get("_source_file", "unknown")
        stats["by_source"][source] += 1
        try:
            val = float(record.get("value", 0))
            stats["value_sum"] += val
            stats["value_count"] += 1
            stats["value_min"] = min(stats["value_min"], val)
            stats["value_max"] = max(stats["value_max"], val)
        except (ValueError, TypeError):
            pass
    # Calcul de la moyenne (évite division par zéro)
    if stats["value_count"] > 0:
        stats["value_mean"] = stats["value_sum"] / stats["value_count"]
    else:
        stats["value_mean"] = 0
    # Conversion des defaultdict en dict normaux (pour la sérialisation JSON)
    stats["by_date"] = dict(stats["by_date"])
    stats["by_bucket"] = dict(stats["by_bucket"])
    stats["by_source"] = dict(stats["by_source"])
    logger.info("Aggregation complete: %d records processed", stats["total_records"])

    # ============================================================
    # STEP 10: Write output files (LOAD)
    # ============================================================
    # Crée le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    # --- Fichier 1 : Données enrichies (le résultat principal) ---
    output_path = os.path.join(output_dir, "enriched_data.json")
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(enriched_records, fh, indent=2, default=str)
    logger.info("Wrote enriched data to %s", output_path)

    # --- Fichier 2 : Records invalides (pour investigation) ---
    invalid_path = os.path.join(output_dir, "invalid_records.json")
    with open(invalid_path, "w", encoding="utf-8") as fh:
        json.dump(invalid_records, fh, indent=2, default=str)
    logger.info("Wrote %d invalid records to %s", len(invalid_records), invalid_path)

    # --- Fichier 3 : Statistiques agrégées ---
    stats_path = os.path.join(output_dir, "pipeline_stats.json")
    with open(stats_path, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, default=str)
    logger.info("Wrote pipeline stats to %s", stats_path)

    # --- Fichier 4 : Manifeste du run (métadonnées) ---
    # Résume ce qui s'est passé pendant ce run du pipeline
    elapsed = time.time() - start_time
    manifest = {
        "pipeline_run": datetime.now().isoformat(),
        "input_dir": input_dir,
        "output_dir": output_dir,
        "source_files": len(source_files),
        "total_raw_records": len(all_records),
        "duplicates_removed": duplicate_count,
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "enriched_records": len(enriched_records),
        "elapsed_seconds": round(elapsed, 2),
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    logger.info("Wrote manifest to %s", manifest_path)

    logger.info("Pipeline completed in %.2f seconds", elapsed)
    return manifest


if __name__ == "__main__":
    # --- Point d'entrée quand on lance directement : python pipeline.py ---
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = run_pipeline("./data/raw", "./data/output")
    print(json.dumps(result, indent=2))
