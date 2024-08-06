import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.utils.auth import AuthenticationChecker, get_current_user
from app.db.database import get_db_session
from app.schemas import ContactResponseSchema
from app.services import (
    follow_user_service,
    unfollow_user_service,
    get_following_service,
    get_followers_service,
    get_relationship_service,
    get_suggestions_service
)

contacts_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@contacts_router.post(
    '/users/{target_user_id}/follow',
    response_model=ContactResponseSchema,
)
def follow_user(target_user_id: str, user_id: str = Query(...), db: Session = Depends(get_db_session)):
    try:
        return follow_user_service(target_user_id, user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while following user: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

@contacts_router.delete(
    '/users/{target_user_id}/unfollow',
    response_model=ContactResponseSchema,
)
def unfollow_user(target_user_id: str, user_id: str = Query(...), db: Session = Depends(get_db_session)):
    try:
        return unfollow_user_service(target_user_id, user_id,db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while unfollowing user: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

@contacts_router.get(
    '/users/{user_id}/following',
    response_model=List[ContactResponseSchema],
)
def get_following(user_id: str, db: Session = Depends(get_db_session), limit: int = 10, offset: int = 0):
    try:
        return get_following_service(user_id, db, limit, offset)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f'Unexpected error while retrieving following list: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

@contacts_router.get(
    '/users/{user_id}/followers',
    response_model=List[ContactResponseSchema],
)
def get_followers(user_id: str, db: Session = Depends(get_db_session), limit: int = 10, offset: int = 0):
    try:
        return get_followers_service(user_id, db, limit, offset)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f'Unexpected error while retrieving followers list: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

@contacts_router.get(
    '/users/{user_id}/relationship/{target_user_id}',
    response_model=ContactResponseSchema,
)
def get_relationship(user_id: str, target_user_id: str,db: Session = Depends(get_db_session)):
    try:
        return get_relationship_service(user_id, target_user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f'Unexpected error while retrieving relationship: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

@contacts_router.get(
    '/users/{user_id}/suggestions',
    response_model=List[ContactResponseSchema],
)
def get_suggestions(user_id: str, db: Session = Depends(get_db_session)):
    try:
        return get_suggestions_service(user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f'Unexpected error while retrieving suggestions: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')
