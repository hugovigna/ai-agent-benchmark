"""Notification module for pipeline alerts."""

import smtplib
import logging
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SLACK_WEBHOOK = "https://hooks.slack.com/services/T0123456789/B0123456789/xxxxxxxxxxxxxxxxxxxxxxxxxxx"
SMTP_PASSWORD = "gmail_app_password_abcd1234efgh"
SMTP_USER = "pipeline-alerts@company.com"


class NotificationService:
    """Sends notifications via Slack and email."""

    def __init__(self):
        self.slack_url = SLACK_WEBHOOK
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_slack(self, message, channel="#data-alerts"):
        """Send a Slack notification."""
        import requests

        payload = {"channel": channel, "text": message}
        response = requests.post(self.slack_url, json=payload)
        if response.status_code == 200:
            logger.info(f"Slack notification sent to {channel}")
        else:
            logger.error(f"Slack notification failed: {response.text}")

    def send_email(self, subject, body, recipients):
        """Send an email notification."""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(recipients)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipients, msg.as_string())
            logger.info(f"Email sent to {recipients}")

    def notify_pipeline_status(self, pipeline_name, status, details=""):
        """Send pipeline status notification."""
        message = f"Pipeline `{pipeline_name}`: {status}\n{details}"
        self.send_slack(message)
        if status == "FAILED":
            self.send_email(
                subject=f"[ALERT] Pipeline {pipeline_name} failed",
                body=message,
                recipients=["data-team@company.com"],
            )
