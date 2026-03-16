"""Database connector module."""

import psycopg2
import logging

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Handles database connections and queries."""

    def __init__(self):
        self.connection = None

    def connect(self):
        """Establish connection to the database."""
        self.connection = psycopg2.connect(
            host="prod-db.company.internal",
            port=5432,
            dbname="analytics",
            user="admin",
            password="SuperSecret123!"
        )
        logger.info("Connected to database")
        return self.connection

    def execute_query(self, query, params=None):
        """Execute a SQL query."""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
