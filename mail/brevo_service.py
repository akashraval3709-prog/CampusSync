"""
CampusSync ERP - Brevo REST API Service
========================================
File: mail/brevo_service.py

Dispatches transactional emails (Welcome Emails, Password Reset OTPs, Alumni OTPs)
via the Brevo (formerly Sendinblue) v3 REST API over standard HTTPS (Port 443).
Bypasses outbound SMTP port blocks (Port 587/465/25) on cloud hosting like Railway, Render, etc.
"""

import os
import json
import base64
import logging
import urllib.request
import urllib.error
from flask import current_app

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def is_brevo_configured():
    """Returns True if BREVO_API_KEY is defined in config or environment."""
    api_key = current_app.config.get('BREVO_API_KEY') or os.getenv('BREVO_API_KEY')
    return bool(api_key and api_key.strip())


def send_brevo_email(to_email, subject, html_content, to_name=None, text_content=None, sender_email=None, sender_name=None, logo_path=None):
    """
    Sends an email using Brevo v3 HTTPS REST API over Port 443.
    
    :param to_email: Recipient email address
    :param subject: Email subject line
    :param html_content: Rendered HTML body
    :param to_name: Recipient full name (optional)
    :param text_content: Plain text version (optional)
    :param sender_email: From address (must be verified in Brevo)
    :param sender_name: From display name
    :param logo_path: Optional path to local logo image file to embed
    :return: (success: bool, info_or_error: str)
    """
    api_key = current_app.config.get('BREVO_API_KEY') or os.getenv('BREVO_API_KEY')
    if not api_key:
        return False, "BREVO_API_KEY is not configured."

    # Resolve sender email & name
    if not sender_email:
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_DEFAULT_SENDER', 'devidparmar8954@gmail.com')
    if not sender_name:
        sender_name = "CampusSync College"

    # If logo exists and HTML contains cid:college_logo, convert to Base64 data URI for instant rendering
    if logo_path and os.path.exists(logo_path) and 'cid:college_logo' in html_content:
        try:
            ext = os.path.splitext(logo_path)[1].lower().replace('.', '')
            if ext == 'jpg':
                ext = 'jpeg'
            with open(logo_path, 'rb') as f:
                b64_logo = base64.b64encode(f.read()).decode('utf-8')
            data_uri = f"data:image/{ext};base64,{b64_logo}"
            html_content = html_content.replace('cid:college_logo', data_uri)
        except Exception as e:
            logger.warning(f"[Brevo Service] Could not convert inline logo to base64: {e}")

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email.strip()
        },
        "to": [
            {
                "email": to_email.strip(),
                "name": to_name.strip() if to_name else to_email.split('@')[0]
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    if text_content:
        payload["textContent"] = text_content

    headers = {
        "accept": "application/json",
        "api-key": api_key.strip(),
        "content-type": "application/json"
    }

    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(BREVO_API_URL, data=data_bytes, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=20) as resp:
            resp_body = resp.read().decode('utf-8')
            logger.info(f"[Brevo API] SUCCESS: Email sent to {to_email}. Response: {resp_body}")
            try:
                resp_json = json.loads(resp_body)
                return True, resp_json.get('messageId', 'SENT')
            except Exception:
                return True, "SENT"

    except urllib.error.HTTPError as http_err:
        try:
            error_body = http_err.read().decode('utf-8', errors='ignore')
            err_json = json.loads(error_body)
            error_msg = f"Brevo HTTP {http_err.code}: {err_json.get('message', error_body)}"
        except Exception:
            error_msg = f"Brevo HTTP {http_err.code}: {http_err.reason}"
        
        logger.error(f"[Brevo API Error] Failed to send email to {to_email}: {error_msg}")
        return False, error_msg

    except Exception as exc:
        logger.error(f"[Brevo API Exception] Failed to send email to {to_email}: {exc}")
        return False, str(exc)
