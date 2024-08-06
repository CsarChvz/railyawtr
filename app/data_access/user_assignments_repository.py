import datetime
from sqlalchemy import and_, asc, not_, select
from sqlalchemy.orm import Session
from app.models import UserAssignment, Question
from app.models.deck import Deck

def get_user_assignments_due_by_prompt(user_id: str, prompt_id: int, today, db: Session):
    return db.query(UserAssignment).join(Question).filter(
        UserAssignment.user_id == user_id,
        UserAssignment.last_reviewed_at <= today,
        Question.prompt_id == prompt_id
    ).all()


def questions_assigned_to_deck(deck_id: int, user_id: str, db: Session):
    return db.query(UserAssignment).filter(UserAssignment.deck_id == deck_id).all()

def assign_questions_to_user_and_deck(user_id: str, deck_id: int, prompt_id: int, questions: list[Question], db: Session) -> list[UserAssignment]:
    assignments = []
    now = datetime.datetime.utcnow()
    yesterday = now - datetime.timedelta(days=1)

    for question in questions:
        assignment = UserAssignment(
            user_id=user_id,
            prompt_id=prompt_id,
            question_id=question.id,
            deck_id=deck_id,
            last_reviewed_at=yesterday,
            interval=1,
            ease_factor=2.5,
            next_review_date=now.date() - datetime.timedelta(days=1)
        )
        db.add(assignment)
        assignments.append(assignment)

    db.commit()
    return assignments

def get_first_assigned_question(user_id: str, deck_id: int, db: Session) -> UserAssignment:
 
    first_assignment = db.query(UserAssignment).filter(
        UserAssignment.user_id == user_id,
        UserAssignment.deck_id == deck_id
    ).order_by(asc(UserAssignment.created_at)).first()
    
    return first_assignment


def get_user_question_assignment(question_assigned:int, db: Session) -> UserAssignment:

    assignment = (
        db.query(UserAssignment)
        .filter(UserAssignment.id == question_assigned)
        .first()
    )
    return assignment


def get_all_question_assignments(deck_id: int, db: Session):
    today = datetime.datetime.now().date()
    return  db.query(UserAssignment).filter(
        UserAssignment.deck_id == deck_id,
        UserAssignment.next_review_date <= today
    ).all()
    
from sqlalchemy import select, and_, not_

def get_unassigned_questions_for_user(deck_id: int, db: Session):
    # Subconsulta para obtener los IDs de las preguntas que ya están asignadas al usuario
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    assigned_question_ids = select(UserAssignment.question_id).filter(
        and_(
            UserAssignment.deck_id == deck.id,
            UserAssignment.user_id == deck.user_id
        )
    ).subquery()

    # Consulta principal para obtener preguntas del prompt que no estén asignadas al usuario
    unassigned_questions = db.query(Question).filter(
        and_(
            Question.prompt_id == deck.prompt_id,
            not_(Question.id.in_(assigned_question_ids))
        )
    ).all()

    return unassigned_questions
