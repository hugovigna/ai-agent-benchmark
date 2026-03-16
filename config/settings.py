"""Configuration settings for the data pipeline.

BRANCHE : feature/update-config
CE QUI A CHANGÉ PAR RAPPORT À main :
  - DATABASE.host : "localhost" → "prod-db.company.internal" (serveur de prod)
  - DATABASE.name : "analytics_db" → "analytics_prod"
  - DATABASE +pool_size et +max_overflow (paramètres de connection pooling)
  - PIPELINE.batch_size : 1000 → 5000 (plus de records par lot)
  - PIPELINE.max_retries : 3 → 5
  - PIPELINE.timeout : 300 → 600 (10 min au lieu de 5)
  - PIPELINE.log_level : "INFO" → "WARNING" (moins verbeux en prod)
  - PIPELINE +enable_profiling

CONFLIT AVEC feature/refactor-config :
  L'autre branche a modifié les MÊMES sections (DATABASE, PIPELINE)
  mais pour renommer des clés et ajouter des commentaires.
  Git ne sait pas combiner les deux → l'agent doit résoudre.
"""

# --- Valeurs mises à jour pour la production ---
DATABASE = {
    "host": "prod-db.company.internal",  # Changé : localhost → serveur prod
    "port": 5432,
    "name": "analytics_prod",            # Changé : analytics_db → analytics_prod
    "schema": "public",
    "pool_size": 10,       # AJOUTÉ : nombre de connexions dans le pool
    "max_overflow": 20,    # AJOUTÉ : connexions supplémentaires autorisées
}

PIPELINE = {
    "batch_size": 5000,           # Changé : 1000 → 5000 (plus performant)
    "max_retries": 5,             # Changé : 3 → 5 (plus résilient)
    "timeout": 600,               # Changé : 300 → 600 (10 minutes)
    "log_level": "WARNING",       # Changé : INFO → WARNING (moins de logs en prod)
    "enable_profiling": True,     # AJOUTÉ : active le profiling de performance
}

STORAGE = {
    "output_dir": "/data/output",
    "temp_dir": "/tmp/pipeline",
    "archive_dir": "/data/archive",
}
