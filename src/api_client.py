"""API client for external data sources.

CE FICHIER : Client HTTP pour récupérer des données depuis une API externe.
PROBLÈME (Challenge 2) : La clé API et le secret sont écrits en dur
directement dans le code (lignes 16-17). Si quelqu'un obtient ces clés,
il peut faire des requêtes API en se faisant passer pour nous.

CE QUE L'AGENT DOIT FAIRE :
- Déplacer API_KEY, API_SECRET et BASE_URL dans un fichier .env
- Utiliser python-dotenv pour les charger
"""

import requests  # Librairie HTTP pour faire des appels API
import logging

logger = logging.getLogger(__name__)

# --- CREDENTIALS HARDCODÉES (à externaliser) ---
# Ces 3 variables ne devraient JAMAIS être dans le code source.
# API_KEY : clé d'authentification auprès du fournisseur de données
# API_SECRET : secret partagé pour signer les requêtes
# BASE_URL : point d'entrée de l'API (celui-ci est moins critique)
API_KEY = "sk-proj-a8f3k29d4m5n6p7q8r9s0t1u2v3w4x5y6z"     # <-- À EXTERNALISER
API_SECRET = "whsec_MIIEvgIBADANBgkqhkiG9w0BAQEFAASC"       # <-- À EXTERNALISER
BASE_URL = "https://api.datavendor.com/v2"


class DataAPIClient:
    """Client pour récupérer et envoyer des données via une API REST."""

    def __init__(self):
        # requests.Session() réutilise la connexion TCP entre les appels
        # (plus performant que de créer une nouvelle connexion à chaque fois)
        self.session = requests.Session()
        # On configure les headers une fois pour toutes les requêtes
        self.session.headers.update({
            "Authorization": f"Bearer {API_KEY}",  # Token d'auth dans le header HTTP
            "X-API-Secret": API_SECRET,             # Secret dans un header custom
            "Content-Type": "application/json",     # On envoie/reçoit du JSON
        })

    def fetch_records(self, endpoint, params=None):
        """Récupère des données depuis l'API (GET).

        endpoint : chemin relatif (ex: "customers", "events/2024")
        params   : paramètres de query string (ex: {"limit": 100, "page": 2})
        """
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Lève une exception si status HTTP >= 400
        logger.info(f"Fetched {len(response.json())} records from {endpoint}")
        return response.json()

    def post_results(self, endpoint, data):
        """Envoie des résultats traités vers l'API (POST).

        Utilisé pour renvoyer les données transformées au fournisseur.
        """
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
