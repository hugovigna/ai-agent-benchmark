<!-- =============================================================================
  TASK.md — Consignes pour le Challenge 2
  L'agent IA lit ce fichier pour savoir quoi faire.
============================================================================= -->

# Challenge 2: Replace Hardcoded Credentials

<!-- POURQUOI C'EST UN PROBLÈME :
     Des credentials (mots de passe, clés API, tokens) sont écrits directement
     dans le code Python. Si ce code est poussé sur GitHub (même en privé),
     ces secrets sont exposés. C'est le problème de sécurité #1 des projets
     open source. GitHub scanne automatiquement les repos pour ça ("secret scanning").

     LA SOLUTION STANDARD :
     Utiliser un fichier .env (non versionné) qui contient les vraies valeurs,
     et python-dotenv pour les charger dans os.environ au démarrage.
     Seul .env.example (avec les noms mais pas les valeurs) est versionné. -->

## Objectif
Remplacer toutes les credentials hardcodées dans le code par des variables d'environnement via `python-dotenv`.

## Fichiers concernés
<!-- Chaque fichier a un type différent de credential :
     1. PostgreSQL : host + user + password (accès base de données)
     2. API : clé + secret (accès service externe)
     3. AWS : access key + secret key (accès cloud Amazon S3)
     4. Slack/SMTP : webhook URL + password email (notifications) -->
1. `src/db_connector.py` — password et credentials PostgreSQL
2. `src/api_client.py` — API key et API secret
3. `src/cloud_storage.py` — AWS access key et secret key
4. `src/notification.py` — Slack webhook URL et SMTP password

## Critères de validation
<!-- Ces critères correspondent exactement aux vérifications faites
     par validate_challenge2.py. Voir les annotations dans ce fichier. -->
1. Aucune credential hardcodée ne reste dans le code source
2. Un fichier `.env.example` est créé avec les noms de variables (sans les valeurs)
3. Un fichier `.gitignore` exclut `.env`
4. Chaque module utilise `python-dotenv` pour charger les variables
5. Le code lève une erreur claire si une variable requise est manquante
6. Les imports et l'initialisation de dotenv sont corrects
