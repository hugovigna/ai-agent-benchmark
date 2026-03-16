"""Notification module for pipeline alerts.

CE FICHIER : Envoie des notifications Slack et email quand le pipeline
a un problème ou finit de tourner.
PROBLÈME (Challenge 2) : Le webhook Slack et le mot de passe SMTP sont
en dur dans le code. Le webhook Slack permettrait à quiconque de poster
des messages dans le channel #data-alerts de l'entreprise.

CE QUE L'AGENT DOIT FAIRE :
- Déplacer SLACK_WEBHOOK, SMTP_PASSWORD, SMTP_USER dans .env
- Utiliser python-dotenv pour les charger
"""

import smtplib   # Module standard Python pour envoyer des emails via SMTP
import logging
from email.mime.text import MIMEText  # Pour construire un email bien formaté

logger = logging.getLogger(__name__)

# --- CREDENTIALS HARDCODÉES (à externaliser) ---
SLACK_WEBHOOK = "https://hooks.slack.com/services/T0123456789/B0123456789/xxxxxxxxxxxxxxxxxxxxxxxxxxx"  # <-- À EXTERNALISER
SMTP_PASSWORD = "gmail_app_password_abcd1234efgh"  # <-- À EXTERNALISER (mot de passe email)
SMTP_USER = "pipeline-alerts@company.com"          # <-- À EXTERNALISER


class NotificationService:
    """Envoie des notifications via Slack et email."""

    def __init__(self):
        self.slack_url = SLACK_WEBHOOK         # URL du webhook Slack
        self.smtp_server = "smtp.gmail.com"    # Serveur SMTP de Gmail
        self.smtp_port = 587                   # Port SMTP avec STARTTLS (chiffré)

    def send_slack(self, message, channel="#data-alerts"):
        """Envoie une notification dans un channel Slack.

        Utilise un "Incoming Webhook" Slack : on fait un POST HTTP
        avec le message en JSON, et Slack l'affiche dans le channel.
        """
        import requests

        payload = {"channel": channel, "text": message}
        response = requests.post(self.slack_url, json=payload)
        if response.status_code == 200:
            logger.info(f"Slack notification sent to {channel}")
        else:
            logger.error(f"Slack notification failed: {response.text}")

    def send_email(self, subject, body, recipients):
        """Envoie un email via SMTP (Gmail).

        Utilise STARTTLS pour chiffrer la connexion.
        recipients : liste d'adresses email (ex: ["alice@co.com", "bob@co.com"])
        """
        msg = MIMEText(body)              # Crée le corps de l'email
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(recipients)

        # Connexion au serveur SMTP avec chiffrement TLS
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()                              # Active le chiffrement
            server.login(SMTP_USER, SMTP_PASSWORD)         # Authentification
            server.sendmail(SMTP_USER, recipients, msg.as_string())
            logger.info(f"Email sent to {recipients}")

    def notify_pipeline_status(self, pipeline_name, status, details=""):
        """Notifie l'équipe du statut d'un pipeline.

        Envoie toujours un message Slack.
        En cas d'échec (FAILED), envoie aussi un email d'alerte
        pour s'assurer que quelqu'un réagit rapidement.
        """
        message = f"Pipeline `{pipeline_name}`: {status}\n{details}"
        self.send_slack(message)
        if status == "FAILED":
            self.send_email(
                subject=f"[ALERT] Pipeline {pipeline_name} failed",
                body=message,
                recipients=["data-team@company.com"],
            )
