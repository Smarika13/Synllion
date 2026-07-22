"""Email delivery helpers."""

import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


def send_registration_otp(recipient: str, otp_code: str) -> None:
    """Send a registration OTP without exposing it in an API response."""
    message = EmailMessage()
    message["Subject"] = "Verify your Synllion email address"
    message["From"] = settings.FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        f"Your Synllion verification code is {otp_code}. " "It expires in 5 minutes."
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        # Background task exceptions must not expose OTPs or take down requests.
        logger.exception("Failed to send registration OTP to %s", recipient)


def send_company_approval(recipient: str, username: str, temp_password: str) -> None:
    """Send login credentials after a company registration is approved."""
    message = EmailMessage()
    message["Subject"] = "Your Synllion company account has been approved"
    message["From"] = settings.FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        "Your company registration has been approved.\n\n"
        f"Username: {username}\n"
        f"Temporary password: {temp_password}\n\n"
        "Please log in and change your password immediately."
    )
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Failed to send approval email to %s", recipient)


def send_company_rejection(recipient: str, reason: str) -> None:
    """Notify a company that their registration was rejected."""
    message = EmailMessage()
    message["Subject"] = "Your Synllion company registration"
    message["From"] = settings.FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        f"Your company registration could not be approved.\n\nReason: {reason}"
    )
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Failed to send rejection email to %s", recipient)
