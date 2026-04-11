import smtplib
import logging
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_TO      = os.getenv("ALERT_TO", "")


def notify_console(message: str):
    """Log alert to console and file."""
    logger.warning(f"🚨 ALERT: {message}")
    print(f"🚨 ALERT: {message}")


def notify_email(subject: str, body: str) -> dict:
    """Send alert email via SMTP."""
    if not all([SMTP_USER, SMTP_PASSWORD, ALERT_TO]):
        return {"sent": False, "reason": "Email not configured in .env"}

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"]    = SMTP_USER
        msg["To"]      = ALERT_TO

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, ALERT_TO, msg.as_string())

        return {"sent": True, "to": ALERT_TO}
    except Exception as e:
        return {"sent": False, "reason": str(e)}


def send_alert(message: str, subject: str = "🚨 DevOps Monitor Alert") -> dict:
    notify_console(message)
    email_result = notify_email(subject, message)
    return {"console": True, "email": email_result}
