import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.data_access import (
    create_feedback,
    get_feedbacks,
    get_feedback_by_id,
    update_feedback,
    delete_feedback,
)
from app.schemas.feedback import FeedbackCreateSchema, FeedbackResponseSchema

logger = logging.getLogger(__name__)

def create_feedback_service(feedback_data: FeedbackCreateSchema, user_id: str, db: Session) -> FeedbackResponseSchema:
    try:
        new_feedback = create_feedback(feedback_data, user_id, db)
        return FeedbackResponseSchema.from_orm(new_feedback)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while creating feedback: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def get_feedbacks_service(skip: int, limit: int, db: Session) -> list[FeedbackResponseSchema]:
    try:
        feedbacks = get_feedbacks(skip, limit, db)
        return [FeedbackResponseSchema.from_orm(feedback) for feedback in feedbacks]
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving feedbacks: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def get_feedback_by_id_service(feedback_id: int, db: Session) -> FeedbackResponseSchema:
    try:
        feedback = get_feedback_by_id(feedback_id, db)
        if feedback is None:
            raise HTTPException(status_code=404, detail='Feedback not found')
        return FeedbackResponseSchema.from_orm(feedback)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving feedback {feedback_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def update_feedback_service(feedback_id: int, feedback_data: FeedbackCreateSchema, db: Session) -> FeedbackResponseSchema:
    try:
        feedback = update_feedback(feedback_id, feedback_data, db)
        if feedback is None:
            raise HTTPException(status_code=404, detail='Feedback not found')
        return FeedbackResponseSchema.from_orm(feedback)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while updating feedback {feedback_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def delete_feedback_service(feedback_id: int, db: Session) -> FeedbackResponseSchema:
    try:
        feedback = delete_feedback(feedback_id, db)
        if feedback is None:
            raise HTTPException(status_code=404, detail='Feedback not found')
        return FeedbackResponseSchema.from_orm(feedback)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while deleting feedback {feedback_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')
