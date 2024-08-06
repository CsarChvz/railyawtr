import os
import logging

from dotenv import load_dotenv
from fastapi import HTTPException
import resend


load_dotenv()

logger = logging.getLogger(__name__)

resend.api_key = os.getenv('RESEND')


def send_email_service(to: str, subject: str, html_content: str):
    params = {
        'from': 'Chop <chop@so.com>', # Change the email with the domain
        'to': [to],
        'subject': subject,
        'html': html_content,
    }
    try:
        email = resend.Emails.send(params)
        return email
    except Exception as e:
        logger.error(f'Failed to send email: {e}')
        raise HTTPException(status_code=500, detail='Failed to send email')