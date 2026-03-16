"""Cloud storage module for S3 operations.

CE FICHIER : Gère l'upload/download de fichiers vers Amazon S3 (stockage cloud).
PROBLÈME (Challenge 2) : Les clés d'accès AWS sont en dur dans le code.
Avec ces clés, quelqu'un pourrait accéder à TOUT le bucket S3 de production
(lire, écrire, supprimer des fichiers dans le data lake).

CE QUE L'AGENT DOIT FAIRE :
- Déplacer aws_access_key_id et aws_secret_access_key dans .env
- Utiliser python-dotenv pour les charger
- Note : boto3 supporte aussi les variables d'env AWS_ACCESS_KEY_ID nativement
"""

import boto3    # SDK officiel d'Amazon Web Services pour Python
import logging

logger = logging.getLogger(__name__)


class CloudStorage:
    """Gère les opérations de stockage sur Amazon S3."""

    def __init__(self):
        # boto3.client("s3") crée un client pour interagir avec le service S3
        # PROBLÈME : les clés sont passées directement ici au lieu de venir
        # de l'environnement ou d'un fichier de config sécurisé
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id="AKIAIOSFODNN7EXAMPLE",                        # <-- À EXTERNALISER
            aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # <-- À EXTERNALISER
            region_name="eu-west-1",  # Région AWS (Irlande)
        )
        self.bucket_name = "company-data-lake-prod"  # Nom du bucket S3

    def upload_file(self, local_path, remote_key):
        """Upload un fichier local vers S3.

        local_path : chemin du fichier sur le disque (ex: "/tmp/output.json")
        remote_key : chemin dans S3 (ex: "pipeline/2024/01/output.json")
        """
        self.s3_client.upload_file(local_path, self.bucket_name, remote_key)
        logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{remote_key}")

    def download_file(self, remote_key, local_path):
        """Télécharge un fichier depuis S3 vers le disque local."""
        self.s3_client.download_file(self.bucket_name, remote_key, local_path)
        logger.info(f"Downloaded s3://{self.bucket_name}/{remote_key} to {local_path}")

    def list_files(self, prefix=""):
        """Liste les fichiers dans le bucket S3.

        prefix : filtre pour ne lister qu'un sous-dossier
                 (ex: "pipeline/2024/" ne liste que les fichiers de 2024)
        Retourne une liste de clés S3 (chemins des fichiers).
        """
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix
        )
        # response["Contents"] contient la liste des objets S3
        # On extrait juste la clé (le chemin) de chaque objet
        return [obj["Key"] for obj in response.get("Contents", [])]
