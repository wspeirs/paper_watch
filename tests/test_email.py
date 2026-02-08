import unittest
from unittest.mock import patch, MagicMock
from paper_watch.reporting.email_client import EmailClient

class TestEmailClient(unittest.TestCase):
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        # Setup environment variables for testing
        with patch.dict('os.environ', {
            'SMTP_HOST': 'smtp.example.com',
            'SMTP_PORT': '587',
            'SMTP_USER': 'user',
            'SMTP_PASSWORD': 'pass',
            'FROM_EMAIL': 'from@example.com'
        }):
            client = EmailClient()
            result = client.send_email(
                to_email="bill.speirs@gmail.com",
                subject="Test Subject",
                body_markdown="Test Body"
            )

            self.assertTrue(result)
            mock_smtp.assert_called_once_with('smtp.example.com', 587)
            instance = mock_smtp.return_value.__enter__.return_value
            instance.starttls.assert_called_once()
            instance.login.assert_called_once_with('user', 'pass')
            instance.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_no_host(self, mock_smtp):
        # Host not set should skip delivery and return True
        with patch.dict('os.environ', {}, clear=True):
            client = EmailClient()
            result = client.send_email(
                to_email="test@example.com",
                subject="Subject",
                body_markdown="Body"
            )
            self.assertTrue(result)
            mock_smtp.assert_not_called()

if __name__ == '__main__':
    unittest.main()
