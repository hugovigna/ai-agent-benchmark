# Challenge 2: Replace Hardcoded Credentials

## Objectif
Remplacer toutes les credentials hardcodées dans le code par des variables d'environnement via `python-dotenv`.

## Fichiers concernés
1. `src/db_connector.py` — password et credentials PostgreSQL
2. `src/api_client.py` — API key et API secret
3. `src/cloud_storage.py` — AWS access key et secret key
4. `src/notification.py` — Slack webhook URL et SMTP password

## Critères de validation
1. Aucune credential hardcodée ne reste dans le code source
2. Un fichier `.env.example` est créé avec les noms de variables (sans les valeurs)
3. Un fichier `.gitignore` exclut `.env`
4. Chaque module utilise `python-dotenv` pour charger les variables
5. Le code lève une erreur claire si une variable requise est manquante
6. Les imports et l'initialisation de dotenv sont corrects
