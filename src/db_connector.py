"""Database connector module.

CE FICHIER : Gère la connexion à PostgreSQL.
PROBLÈME (Challenge 2) : Les credentials (host, user, password) sont
écrites EN DUR dans le code source (ligne 23 : password="SuperSecret123!").
C'est une faille de sécurité majeure — si ce fichier est poussé sur GitHub,
n'importe qui peut accéder à la base de données.

CE QUE L'AGENT DOIT FAIRE :
1. Remplacer les valeurs hardcodées par des os.getenv() ou dotenv
2. Créer un .env.example avec les noms des variables (sans les valeurs)
3. S'assurer qu'une erreur claire est levée si une variable manque
"""

import psycopg2  # Driver Python pour PostgreSQL
import logging

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Gère les connexions et requêtes vers PostgreSQL."""

    def __init__(self):
        self.connection = None  # La connexion sera créée à la demande (lazy)

    def connect(self):
        """Établit la connexion à la base de données.

        PROBLÈME ICI : Toutes les credentials sont en dur dans le code.
        host, dbname, user, password — tout est visible en clair.
        Un attaquant qui lit ce fichier a un accès complet à la DB.
        """
        self.connection = psycopg2.connect(
            host="prod-db.company.internal",  # <-- CREDENTIAL HARDCODÉE
            port=5432,
            dbname="analytics",               # <-- CREDENTIAL HARDCODÉE
            user="admin",                     # <-- CREDENTIAL HARDCODÉE
            password="SuperSecret123!"        # <-- CREDENTIAL HARDCODÉE (le pire)
        )
        logger.info("Connected to database")
        return self.connection

    def execute_query(self, query, params=None):
        """Exécute une requête SQL et retourne les résultats.

        - Si pas encore connecté, se connecte automatiquement (lazy connection)
        - params : paramètres pour les requêtes préparées (protection contre SQL injection)
        """
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query, params)  # Requête paramétrée = sécurisé contre injection SQL
        return cursor.fetchall()

    def close(self):
        """Ferme proprement la connexion à la base."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
