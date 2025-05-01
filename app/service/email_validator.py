import smtplib
from email.message import EmailMessage
import os
from utils import load_environment

load_environment()

EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")


def send_reset_email(to_email, username, reset_token):
    message = EmailMessage()
    message["Subject"] = "Password Reset Request"
    message["From"] = EMAIL
    message["To"] = to_email

    message.set_content(
        f"""
      <html>
        <body>
            <p>Hi {username},<br><br>
               You requested a password reset.<br>
               Copy the token below to reset your password:<br>
               <strong>{reset_token}</strong><br><br>
               This token will expire in 20 minutes. If you did not request this reset, you can safely ignore this email..<br><br>
               Kind Regards,<br>
               Your App Team
            </p>
        </body>
    </html>
    """,
        subtype="html",
    )

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL, APP_PASSWORD)
            smtp.send_message(message)
    except Exception as e:
        print("Email sending failed:", e)
