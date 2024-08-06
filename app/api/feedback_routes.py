import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.utils.auth import AuthenticationChecker, get_current_user
from app.db.database import get_db_session
from app.schemas import FeedbackCreateSchema, FeedbackResponseSchema, FeedbackBaseSchema
from app.services import (
    create_feedback_service,
    get_feedbacks_service,
    get_feedback_by_id_service,
    update_feedback_service,
    delete_feedback_service,
)

feedback_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@feedback_router.post(
    '/',
    response_model=FeedbackResponseSchema,
    status_code=201,
)
def create_feedback(
    feedback_data: FeedbackBaseSchema,
    user_id: str = Query(...),
    db: Session = Depends(get_db_session),
):
    try:
        return create_feedback_service(feedback_data, user_id,db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while creating feedback: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

@feedback_router.get(
    '/',
    response_model=List[FeedbackResponseSchema],
)
def get_feedbacks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
):
    try:
        return get_feedbacks_service(skip, limit, db)
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=500, detail='Internal server error')

@feedback_router.get(
    '/{feedback_id}',
    response_model=FeedbackResponseSchema,
)
def get_feedback_by_id(
    feedback_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return get_feedback_by_id_service(feedback_id, db)
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=500, detail='Internal server error')

@feedback_router.put(
    '/{feedback_id}',
    response_model=FeedbackResponseSchema,
)
def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackCreateSchema,
    db: Session = Depends(get_db_session),
):
    try:
        return update_feedback_service(feedback_id, feedback_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while updating feedback: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

@feedback_router.delete(
    '/{feedback_id}',
    response_model=FeedbackResponseSchema,
)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return delete_feedback_service(feedback_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while deleting feedback: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')
