import logging
import os
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

class EmailClient:
    """Sends emails using the SendGrid Python SDK."""
    
    def __init__(self):
        self.sendgrid_api_key = os.environ.get("SENDGRID_KEY")
        self.from_email = os.environ.get("FROM_EMAIL")

        if not self.sendgrid_api_key:
            raise ValueError("SENDGRID_KEY environment variable is not set")
        if not self.from_email:
            raise ValueError("FROM_EMAIL environment variable is not set")

    def send_email(self, to_email: str, subject: str, body_markdown: str, body_html: Optional[str] = None) -> bool:
        """Sends an email using SendGrid SDK."""
        if not self.sendgrid_api_key:
            logger.warning("SENDGRID_SECRET not set. Skipping email delivery. Printing to log.")
            logger.info(f"EMAIL TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            logger.info(f"BODY:\n{body_markdown}")
            return True

        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body_markdown,
                html_content=body_html if body_html else body_markdown
            )

            # Using the SECRET as the API Key for the client
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            if 200 <= response.status_code < 300:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status Code: {response.status_code}, Body: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    
    client = EmailClient()
    test_to = os.environ.get("RECIPIENT_EMAIL", "bill.speirs@gmail.com")
    
    print(f"Testing SendGrid with:")
    print(f"  API Key: {client.sendgrid_api_key[:5]}...{client.sendgrid_api_key[-5:] if client.sendgrid_api_key else 'None'}")
    print(f"  From: {client.from_email}")
    print(f"  To: {test_to}")
    
    success = client.send_email(
        to_email=test_to,
        subject="SendGrid Test Connection",
        body_markdown="This is a test email from the Paper Watch Bot."
    )
    
    if success:
        print("SUCCESS: Test email sent.")
    else:
        print("FAILURE: Check logs for details.")
