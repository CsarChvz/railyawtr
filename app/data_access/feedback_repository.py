from sqlalchemy.orm import Session
from app.models import Feedback
from app.schemas import FeedbackCreateSchema

def create_feedback(feedback_data: FeedbackCreateSchema, user_id:str, db: Session) -> Feedback:
    new_feedback = Feedback(
        user_id=user_id,
        message=feedback_data.message
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

def get_feedbacks(skip: int, limit: int, db: Session) -> list[Feedback]:
    return db.query(Feedback).offset(skip).limit(limit).all()

def get_feedback_by_id(feedback_id: int, db: Session) -> Feedback:
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

def update_feedback(feedback_id: int, feedback_data: FeedbackCreateSchema, db: Session) -> Feedback:
    feedback = get_feedback_by_id(feedback_id, db)
    if feedback is None:
        return None
    for key, value in feedback_data.dict(exclude_unset=True).items():
        setattr(feedback, key, value)
    db.commit()
    db.refresh(feedback)
    return feedback

def delete_feedback(feedback_id: int, db: Session) -> Feedback:
    feedback = get_feedback_by_id(feedback_id, db)
    if feedback is None:
        return None
    db.delete(feedback)
    db.commit()
    return feedback
