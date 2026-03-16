"""Configuration settings for the data pipeline.

BRANCHE : feature/refactor-config
CE QUI A CHANGÉ PAR RAPPORT À main :
  STRUCTURE :
  - Ajouté des commentaires de section ("# -- Database Configuration --")
  - Meilleure organisation du fichier par domaine

  RENOMMAGES :
  - DATABASE["name"] → DATABASE["database_name"] (plus explicite)
  - PIPELINE["timeout"] → PIPELINE["timeout_seconds"] (unité dans le nom)

  AJOUTS DE CLÉS :
  - DATABASE +connection_timeout (timeout de connexion)
  - PIPELINE +parallel_workers (nombre de workers parallèles)
  - PIPELINE.batch_size : 1000 → 2000 (légère augmentation)
  - STORAGE +retention_days (durée de rétention des archives)

  NOUVELLES SECTIONS :
  - MONITORING : config Prometheus pour les métriques
  - ALERTING : config des alertes (seuils, canaux)

CONFLIT AVEC feature/update-config :
  L'autre branche a modifié les MÊMES sections (DATABASE, PIPELINE)
  mais pour mettre des valeurs de production (host, batch_size, timeout...).
  Git ne sait pas combiner les deux → l'agent doit résoudre.

Organized by concern: database, pipeline execution, storage, monitoring.
"""

# -- Database Configuration --
DATABASE = {
    "host": "localhost",
    "port": 5432,
    "database_name": "analytics_db",   # Renommé : "name" → "database_name"
    "schema": "public",
    "connection_timeout": 30,          # AJOUTÉ : timeout de connexion en secondes
}

# -- Pipeline Execution --
PIPELINE = {
    "batch_size": 2000,           # Changé : 1000 → 2000
    "max_retries": 3,
    "timeout_seconds": 300,       # Renommé : "timeout" → "timeout_seconds"
    "log_level": "INFO",
    "parallel_workers": 4,        # AJOUTÉ : nombre de workers en parallèle
}

# -- Storage Paths --
STORAGE = {
    "output_dir": "/data/output",
    "temp_dir": "/tmp/pipeline",
    "archive_dir": "/data/archive",
    "retention_days": 90,         # AJOUTÉ : supprimer les archives après 90 jours
}

# -- Monitoring --
# NOUVELLE SECTION : configuration pour les métriques Prometheus
# Permet de surveiller la santé et la performance du pipeline
MONITORING = {
    "enabled": True,
    "metrics_port": 9090,              # Port exposé pour le scraping Prometheus
    "health_check_interval": 30,       # Vérification toutes les 30 secondes
    "export_format": "prometheus",     # Format des métriques
}

# -- Alerting --
# NOUVELLE SECTION : configuration des alertes automatiques
# Déclenche des notifications si le pipeline a des problèmes
ALERTING = {
    "enabled": True,
    "channels": ["slack", "email"],     # Canaux de notification
    "error_threshold": 5,              # Alerte après 5 erreurs
    "latency_threshold_ms": 5000,      # Alerte si latence > 5 secondes
}
