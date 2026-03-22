"""
Real email sending service using SMTP.
Configure via environment variables:
  SMTP_HOST     – e.g. smtp.gmail.com
  SMTP_PORT     – e.g. 587
  SMTP_USER     – your-email@gmail.com
  SMTP_PASSWORD  – app-specific password (NOT your real password)

For Gmail: enable 2-Factor Auth, then create an App Password at
https://myaccount.google.com/apppasswords
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_real_email(to_email: str, subject: str, body: str) -> dict:
    """Send an actual email via SMTP. Returns status dict."""
    # Read env vars inside the function so load_dotenv() from config.py
    # has already been called before we access them
    from app.config import SUPABASE_URL  # noqa – triggers load_dotenv()

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_user or not smtp_password:
        return {
            "sent": False,
            "error": "SMTP not configured. Set SMTP_USER and SMTP_PASSWORD env vars.",
            "fallback": True,
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_email

        # Plain text version
        plain = body

        # Simple HTML version
        html_body = body.replace("\n", "<br>")
        html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
            <div style="background: linear-gradient(135deg, #6366f1, #818cf8); color: white; padding: 24px; border-radius: 12px 12px 0 0;">
                <h2 style="margin: 0;">CareerMatch</h2>
                <p style="margin: 4px 0 0; opacity: 0.9;">Application Update</p>
            </div>
            <div style="background: #fff; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="color: #333; line-height: 1.7; font-size: 15px;">{html_body}</p>
            </div>
            <p style="text-align: center; color: #888; font-size: 12px; margin-top: 16px;">
                Sent via CareerMatch Platform
            </p>
        </div>
        """

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())

        return {"sent": True, "to": to_email, "subject": subject}

    except Exception as e:
        return {"sent": False, "error": str(e)}
