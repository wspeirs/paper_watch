import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)

class EmailClient:
    def __init__(self):
        self.smtp_host = os.environ.get("SMTP_HOST")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER")
        self.smtp_password = os.environ.get("SMTP_PASSWORD")
        self.from_email = os.environ.get("FROM_EMAIL", "paperwatch@example.com")

    def send_email(self, to_email: str, subject: str, body_markdown: str, body_html: Optional[str] = None) -> bool:
        """Sends an email using SMTP."""
        if not self.smtp_host:
            logger.warning("SMTP_HOST not set. Skipping email delivery. Printing to log.")
            logger.info(f"EMAIL TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            logger.info(f"BODY:\n{body_markdown}")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            part1 = MIMEText(body_markdown, "plain")
            msg.attach(part1)

            if body_html:
                part2 = MIMEText(body_html, "html")
                msg.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

# Placeholder for SendGrid if decided later
class SendGridClient(EmailClient):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.environ.get("SENDGRID_API_KEY")

    def send_email(self, to_email: str, subject: str, body_markdown: str, body_html: Optional[str] = None) -> bool:
        # Implementation would go here using sendgrid library
        logger.info(f"SendGrid send_email called for {to_email}")
        return super().send_email(to_email, subject, body_markdown, body_html)