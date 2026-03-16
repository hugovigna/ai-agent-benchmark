"""API client for external data sources."""

import requests
import logging

logger = logging.getLogger(__name__)

API_KEY = "sk-proj-a8f3k29d4m5n6p7q8r9s0t1u2v3w4x5y6z"
API_SECRET = "whsec_MIIEvgIBADANBgkqhkiG9w0BAQEFAASC"
BASE_URL = "https://api.datavendor.com/v2"


class DataAPIClient:
    """Client for fetching data from external API."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {API_KEY}",
            "X-API-Secret": API_SECRET,
            "Content-Type": "application/json",
        })

    def fetch_records(self, endpoint, params=None):
        """Fetch records from the API."""
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        logger.info(f"Fetched {len(response.json())} records from {endpoint}")
        return response.json()

    def post_results(self, endpoint, data):
        """Post processed results back to the API."""
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
