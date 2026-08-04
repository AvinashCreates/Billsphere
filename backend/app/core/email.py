import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Sends an email via SMTP. Returns True/False, never raises —
    callers (Celery tasks) decide whether to retry."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        logger.error("SMTP not configured — skipping email to %s", to_email)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, [to_email], msg.as_string())
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False