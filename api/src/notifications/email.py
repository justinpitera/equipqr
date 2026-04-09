"""
notifications/email.py - Infrastructure layer for outbound email delivery.

Knows *how* to send an email (SMTP or Resend) but nothing about auth logic
or HTTP requests.
"""

import datetime
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import LiteralString

import resend
from loguru import logger

from src import API_CONFIG

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BASE_URL: str = API_CONFIG["api"]["domain"]

_SUBJECT_LINES: list[str] = [
    "Your Aviator Account Awaits – Streamline Equipment Reporting Today",
    "Quick! Your Aviator Account is Ready to Transform Ground Operations",
    "Empower Your Workflow with Aviator – Get Started Now",
    "Aviator Access: Your Solution for Seamless Issue Reporting",
    "Your Aviator Account is Ready – Simplify Ground Equipment Checks",
    "Set Up Aviator and Become a Ground Operations Hero",
    "Aviator: The Key to Efficient Equipment Maintenance",
    "Your Aviator Account is Waiting – Start Scanning with Ease",
    "Aviator Awaits: Simplify, Scan, and Report with Confidence",
    "Don't Keep Aviator Waiting – Streamline Maintenance Today",
    "Unlock Aviator Access – A Smarter Way to Report and Resolve Issues",
    "Your Exclusive Invitation to Aviator's Advanced Reporting Tools",
    "Aviator: Turning Ground Equipment Checks into a Breeze",
    "Aviator Setup – Enhance Ground Crew Efficiency in Minutes",
    "Your Aviator Account is Ready – Let's Get Ground Equipment Right",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_magic_link_html(set_token_link: str) -> str:
    user_message: LiteralString = "Click the button below to securely access your Aviator account."
    year = datetime.date.today().year
    return (
        f"<html><body style='font-family: Segoe UI, Tahoma, sans-serif; background-color: #121212; color: #e0e0e0; padding: 40px; margin: 0;'>"
        f"<div style='max-width: 600px; margin: auto; background-color: #1e1e1e; border-radius: 8px; overflow: hidden; box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);'>"
        f"<div style='padding: 20px; text-align: center; border-bottom: 1px solid #333;'>"
        f"<h2 style='margin: 0; color: #ffffff;'>Aviator</h2></div>"
        f"<div style='padding: 30px; text-align: center;'>"
        f"<p style='font-size: 15px; line-height: 1.6; margin-bottom: 20px;'>{user_message}</p>"
        f"<a href='{set_token_link}' style='background-color: #0078D7; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 14px;'>"
        f"Access Aviator</a>"
        f"<p style='margin-top: 30px; font-size: 13px; color: #b3b3b3;'>If you did not request this email, please ignore it.</p></div>"
        f"<div style='padding: 15px; background-color: #161616; text-align: center; font-size: 11px; color: #666;'>"
        f"© {year} Aviator<br>All rights reserved.</div></div></body></html>"
    )


def _send_via_smtp(to: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart(_subtype="related")
    msg["Subject"] = subject
    msg["From"] = f"no-reply@{API_CONFIG['smtp']['domain']}"
    msg["To"] = to
    msg.attach(MIMEText(_text=html_body, _subtype="html"))

    try:
        with smtplib.SMTP(host=API_CONFIG["smtp"]["host"], port=API_CONFIG["smtp"]["port"]) as server:
            server.starttls()
            server.login(user=API_CONFIG["smtp"]["username"], password=API_CONFIG["smtp"]["password"])
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        raise RuntimeError("Authentication with the SMTP server failed")
    except smtplib.SMTPConnectError as e:
        logger.error(f"Failed to connect to the SMTP server: {e}")
        raise RuntimeError("Unable to connect to the SMTP server")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise RuntimeError("An error occurred while sending the email")
    except Exception as e:
        logger.error(f"Unexpected SMTP error: {e}")
        raise RuntimeError("An unexpected error occurred while sending the email")


def _send_via_resend(to: str, subject: str, html_body: str) -> None:
    resend.api_key = API_CONFIG["smtp"]["resend"]["api_key"]
    try:
        resend.Emails.send({
            "from": API_CONFIG["smtp"]["resend"]["from_email"],
            "to": [to],
            "subject": subject,
            "html": html_body,
        })
    except Exception as e:
        logger.error(f"Resend error: {e}")
        raise RuntimeError("An error occurred while sending the email via Resend")


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def send_magic_link_email(email: str, set_token_link: str) -> None:
    """
    Deliver a magic-link email to *email* using whichever provider is
    configured (SMTP or Resend).

    This function is deliberately synchronous so it can be offloaded to a
    thread-pool by the caller if needed.
    """
    subject = random.choice(_SUBJECT_LINES)
    html_body = _build_magic_link_html(set_token_link)
    provider: str = API_CONFIG["smtp"].get("provider", "smtp")

    if provider == "resend":
        _send_via_resend(to=email, subject=subject, html_body=html_body)
    else:
        _send_via_smtp(to=email, subject=subject, html_body=html_body)
