import smtplib
from email.message import EmailMessage
import os
from utils import load_environment

load_environment()

EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def send_reset_email(to_email, reset_link):
    message = EmailMessage()
    message["Subject"] = "Social Media Account Password Reset Request"
    message["From"] = EMAIL
    message["To"] = to_email

    message.set_content(
        f"""
    Hi,
                    
    You requested a password reset. Click the link below to reset your password:
    {reset_link}

    If you did not request this, please ignore this email.

    Kind regards,
    Social Media App team


                """
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(message)
