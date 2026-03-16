"""Long-running pipeline with 10 sequential steps — no checkpointing.

CE FICHIER : Pipeline en 10 étapes séquentielles — c'est le coeur du Challenge 4.
PROBLÈME : Si le pipeline plante à l'étape 7 (ex: API timeout, erreur réseau),
il faut TOUT recommencer depuis l'étape 1. Sur un vrai pipeline qui prend
30 minutes, c'est un énorme gaspillage de temps et de ressources.

CE QUE L'AGENT DOIT FAIRE :
Ajouter un système de "checkpointing" :
  1. Après chaque étape réussie, sauvegarder l'état (context) sur disque en JSON
  2. Au démarrage, vérifier s'il existe un checkpoint → reprendre où on s'est arrêté
  3. Après un run complet réussi, nettoyer les fichiers de checkpoint
  4. Permettre un --force-restart pour ignorer les checkpoints

ANALOGIE : C'est comme les sauvegardes dans un jeu vidéo.
Sans checkpoint = recommencer au niveau 1 à chaque game over.
Avec checkpoint = reprendre au dernier point de sauvegarde.

ARCHITECTURE DU PIPELINE :
  Étape 1  : Récupérer les données sources (CRM, ERP, web analytics)
  Étape 2  : Valider les schémas des données
  Étape 3  : Dédupliquer les records
  Étape 4  : Nettoyer les données (nulls, formats)
  Étape 5  : Appliquer les règles métier
  Étape 6  : Enrichir avec des données externes (API lente)
  Étape 7  : Calculer les agrégats et KPIs
  Étape 8  : Générer les rapports
  Étape 9  : Charger dans le data warehouse
  Étape 10 : Envoyer les notifications de fin

NOTE : Les time.sleep() et random.randint() simulent des opérations
réelles (appels réseau, calculs longs). Le context dict passe d'étape
en étape et accumule les résultats.
"""

import os
import json
import time
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# ÉTAPE 1 : Récupération des données sources
# =============================================================================
def step_01_fetch_sources(context):
    """Simule la récupération de données depuis 3 systèmes sources.

    En production, ça ferait de vrais appels API/DB vers le CRM,
    l'ERP et le système de web analytics.
    Le time.sleep(0.5) simule la latence réseau.
    """
    logger.info("Step 1/10: Fetching sources...")
    time.sleep(0.5)  # Simule un appel réseau
    # Simule des volumes de données aléatoires
    context["sources"] = [
        {"name": "crm", "records": random.randint(1000, 5000)},
        {"name": "erp", "records": random.randint(2000, 8000)},
        {"name": "web_analytics", "records": random.randint(5000, 20000)},
    ]
    context["raw_count"] = sum(s["records"] for s in context["sources"])
    logger.info("Fetched %d total records from %d sources",
                context["raw_count"], len(context["sources"]))
    return context


# =============================================================================
# ÉTAPE 2 : Validation des schémas
# =============================================================================
def step_02_validate_schemas(context):
    """Vérifie que les données sources ont les bonnes colonnes.

    En production, ça vérifierait que chaque source a bien les champs
    attendus (id, timestamp, value, category) avec les bons types.
    Ici c'est simulé — tout passe toujours.
    """
    logger.info("Step 2/10: Validating schemas...")
    time.sleep(0.3)
    expected_fields = {"id", "timestamp", "value", "category"}
    context["schema_valid"] = True
    for source in context["sources"]:
        source["schema_ok"] = True  # Simulé : en vrai on vérifierait le schéma
    logger.info("All schemas validated successfully")
    return context


# =============================================================================
# ÉTAPE 3 : Déduplication
# =============================================================================
def step_03_deduplicate(context):
    """Supprime les doublons entre les différentes sources.

    Un même client peut apparaître dans le CRM ET dans le web analytics.
    On simule un taux de doublons entre 5% et 15%.
    """
    logger.info("Step 3/10: Deduplicating...")
    time.sleep(0.4)
    dup_rate = random.uniform(0.05, 0.15)  # 5% à 15% de doublons
    context["duplicates_removed"] = int(context["raw_count"] * dup_rate)
    context["deduped_count"] = context["raw_count"] - context["duplicates_removed"]
    logger.info("Removed %d duplicates", context["duplicates_removed"])
    return context


# =============================================================================
# ÉTAPE 4 : Nettoyage des données
# =============================================================================
def step_04_clean_data(context):
    """Nettoie les données : remplit les nulls, corrige les formats.

    Exemples de nettoyage en production :
    - Dates dans des formats différents → standardiser en ISO 8601
    - "N/A", "", "null" → None
    - Espaces en trop, caractères spéciaux
    """
    logger.info("Step 4/10: Cleaning data...")
    time.sleep(0.6)
    context["null_filled"] = random.randint(50, 500)      # Nulls remplacés
    context["format_fixed"] = random.randint(100, 1000)    # Formats corrigés
    context["clean_count"] = context["deduped_count"]
    logger.info("Filled %d nulls, fixed %d format issues",
                context["null_filled"], context["format_fixed"])
    return context


# =============================================================================
# ÉTAPE 5 : Application des règles métier
# =============================================================================
def step_05_apply_business_rules(context):
    """Applique les règles métier et filtre les records non conformes.

    Exemples de règles métier :
    - Rejeter les transactions de montant négatif
    - Exclure les comptes de test
    - Appliquer des conversions de devises
    On simule un taux de rejet entre 1% et 5%.
    """
    logger.info("Step 5/10: Applying business rules...")
    time.sleep(0.5)
    reject_rate = random.uniform(0.01, 0.05)  # 1% à 5% de rejet
    context["rejected_by_rules"] = int(context["clean_count"] * reject_rate)
    context["rules_passed"] = context["clean_count"] - context["rejected_by_rules"]
    logger.info("Applied rules: %d passed, %d rejected",
                context["rules_passed"], context["rejected_by_rules"])
    return context


# =============================================================================
# ÉTAPE 6 : Enrichissement avec données externes
# =============================================================================
def step_06_enrich_external(context):
    """Enrichit chaque record avec des données de référence externes.

    En production, ça appellerait une API externe (ex: géolocalisation,
    scoring client, données de marché). C'est souvent l'étape la plus
    lente car elle dépend d'un service tiers.
    Le time.sleep(0.8) simule cette latence.
    """
    logger.info("Step 6/10: Enriching with external data...")
    time.sleep(0.8)  # API externe = lent
    context["enriched_count"] = context["rules_passed"]
    context["enrichment_fields_added"] = ["geo_region", "customer_segment", "risk_score"]
    logger.info("Enriched %d records with %d fields",
                context["enriched_count"], len(context["enrichment_fields_added"]))
    return context


# =============================================================================
# ÉTAPE 7 : Calcul des agrégats
# =============================================================================
def step_07_compute_aggregates(context):
    """Calcule les métriques agrégées et KPIs.

    KPI = Key Performance Indicator (indicateur clé de performance)
    Exemples : chiffre d'affaires total, panier moyen, répartition par catégorie.
    """
    logger.info("Step 7/10: Computing aggregates...")
    time.sleep(0.4)
    context["aggregates"] = {
        "total_value": round(random.uniform(100000, 999999), 2),
        "avg_value": round(random.uniform(10, 500), 2),
        "category_counts": {"A": random.randint(100, 1000),
                            "B": random.randint(100, 1000),
                            "C": random.randint(100, 1000)},
    }
    logger.info("Computed aggregates: total_value=%.2f", context["aggregates"]["total_value"])
    return context


# =============================================================================
# ÉTAPE 8 : Génération des rapports
# =============================================================================
def step_08_generate_reports(context):
    """Génère les rapports de synthèse.

    En production, ça créerait des fichiers JSON/CSV/HTML avec les
    résumés du traitement (ex: rapport journalier, ventilation par catégorie).
    """
    logger.info("Step 8/10: Generating reports...")
    time.sleep(0.3)
    context["reports"] = [
        "daily_summary.json",
        "category_breakdown.json",
        "anomaly_report.json",
    ]
    logger.info("Generated %d reports", len(context["reports"]))
    return context


# =============================================================================
# ÉTAPE 9 : Chargement dans le data warehouse
# =============================================================================
def step_09_load_to_warehouse(context):
    """Charge les données traitées dans le data warehouse.

    En production, ça ferait un COPY ou INSERT en bulk dans PostgreSQL,
    BigQuery, Snowflake ou Redshift. C'est souvent lent car on insère
    des milliers/millions de lignes.
    """
    logger.info("Step 9/10: Loading to warehouse...")
    time.sleep(0.7)  # Simule un bulk insert lent
    context["loaded_count"] = context["enriched_count"]
    context["load_table"] = "analytics.fact_events"
    logger.info("Loaded %d records to %s",
                context["loaded_count"], context["load_table"])
    return context


# =============================================================================
# ÉTAPE 10 : Notifications de fin
# =============================================================================
def step_10_notify_completion(context):
    """Envoie les notifications de fin de pipeline.

    Prévient l'équipe data que le pipeline a terminé avec succès
    via Slack et email.
    """
    logger.info("Step 10/10: Sending notifications...")
    time.sleep(0.2)
    context["notifications_sent"] = ["slack", "email"]
    context["pipeline_status"] = "SUCCESS"
    context["completed_at"] = datetime.now().isoformat()
    logger.info("Pipeline completed successfully")
    return context


# =============================================================================
# REGISTRE DES ÉTAPES
# =============================================================================
# Liste ordonnée de toutes les fonctions d'étape.
# C'est ce qui permet à run_long_pipeline() de les exécuter en boucle.
# L'agent devra modifier cette boucle pour ajouter le checkpointing.
PIPELINE_STEPS = [
    step_01_fetch_sources,
    step_02_validate_schemas,
    step_03_deduplicate,
    step_04_clean_data,
    step_05_apply_business_rules,
    step_06_enrich_external,
    step_07_compute_aggregates,
    step_08_generate_reports,
    step_09_load_to_warehouse,
    step_10_notify_completion,
]


# =============================================================================
# ORCHESTRATEUR PRINCIPAL
# =============================================================================
def run_long_pipeline():
    """Exécute les 10 étapes du pipeline en séquence.

    PROBLÈME ACTUEL :
    Si une étape échoue (exception), on fait raise → le pipeline s'arrête.
    Au prochain lancement, on recommence TOUT depuis l'étape 1.
    Il n'y a aucune mémoire de ce qui a déjà été fait.

    CE QUI MANQUE (= le challenge) :
    - Sauvegarde du context après chaque étape réussie
    - Détection d'un checkpoint existant au démarrage
    - Reprise à la dernière étape réussie + 1
    - Nettoyage des checkpoints après succès complet

    Le "context" est un dictionnaire qui s'enrichit à chaque étape.
    Chaque step_XX reçoit le context, ajoute ses résultats, et le retourne.
    """
    start_time = time.time()
    context = {
        "pipeline_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "started_at": datetime.now().isoformat(),
    }
    logger.info("Starting pipeline %s", context["pipeline_id"])

    # --- Boucle principale : exécute chaque étape dans l'ordre ---
    # enumerate(PIPELINE_STEPS, 1) → donne (1, step_01), (2, step_02), etc.
    for i, step_fn in enumerate(PIPELINE_STEPS, 1):
        try:
            context = step_fn(context)
            # ICI IL FAUDRAIT SAUVEGARDER LE CHECKPOINT
            # (c'est ce que l'agent doit ajouter)
        except Exception as e:
            logger.error("Pipeline failed at step %d/%d (%s): %s",
                         i, len(PIPELINE_STEPS), step_fn.__name__, e)
            context["pipeline_status"] = "FAILED"
            context["failed_step"] = i
            context["error"] = str(e)
            raise  # Relance l'exception → le pipeline s'arrête

    elapsed = time.time() - start_time
    context["elapsed_seconds"] = round(elapsed, 2)
    logger.info("Full pipeline completed in %.2f seconds", elapsed)
    return context


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================
if __name__ == "__main__":
    # Configuration du logging pour voir les messages dans le terminal
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    result = run_long_pipeline()
    # Affiche le résultat final en JSON indenté
    print(json.dumps(result, indent=2, default=str))
