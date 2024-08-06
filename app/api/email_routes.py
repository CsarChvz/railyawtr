import logging
from typing import List
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session


from app.services import (
    send_email_service
)


email_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
SECRET_KEY = os.getenv('SECRET_KEY')


@email_router.post('/send-email/')
def send_email(to: str, subject: str, html_content: str, secret_key: str = Query(...)):
    if(secret_key == SECRET_KEY):
        try:
            return send_email_service(to, subject, html_content)
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f'Unexpected error while creating user: {e}')
            raise HTTPException(status_code=500, detail='Internal server error')
    
    else:
        raise HTTPException(status_code=400, detail='Unaturoized')

