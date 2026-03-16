"""Configuration settings for the data pipeline.

CE FICHIER : Configuration centrale du pipeline de données.
C'est le fichier qui sera au coeur du Challenge 1 (merge conflict).
Deux branches le modifient différemment :
  - feature/update-config : change les VALEURS (batch_size 1000→5000, etc.)
  - feature/refactor-config : change la STRUCTURE (ajoute MONITORING, ALERTING, renomme des clés)
Quand on essaie de merger les deux branches, Git ne sait pas comment
combiner les deux modifications → conflit à résoudre.
"""

# --- Connexion à la base de données PostgreSQL ---
# En vrai, ces valeurs seraient dans un .env ou un vault,
# mais ici on les laisse simples pour le challenge 1.
DATABASE = {
    "host": "localhost",       # Adresse du serveur PostgreSQL
    "port": 5432,              # Port par défaut de PostgreSQL
    "name": "analytics_db",    # Nom de la base de données
    "schema": "public",        # Schéma PostgreSQL utilisé
}

# --- Paramètres d'exécution du pipeline ---
PIPELINE = {
    "batch_size": 1000,   # Nombre de records traités par lot
    "max_retries": 3,     # Nombre de tentatives en cas d'erreur
    "timeout": 300,       # Timeout en secondes (5 minutes)
    "log_level": "INFO",  # Niveau de log (DEBUG, INFO, WARNING, ERROR)
}

# --- Chemins de stockage des fichiers ---
STORAGE = {
    "output_dir": "/data/output",     # Où écrire les résultats finaux
    "temp_dir": "/tmp/pipeline",      # Fichiers temporaires pendant le traitement
    "archive_dir": "/data/archive",   # Archive des anciens runs
}
