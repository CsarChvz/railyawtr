import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.data_access import (
    user_assignments_repository, 
    questions_assigned_to_deck,
    assign_questions_to_user_and_deck,
    get_first_assigned_question,
    get_user_question_assignment,
    get_all_question_assignments,
    get_unassigned_questions_for_user
    )
from app.models.option import Option
from app.models.question import Question
from app.schemas import UserAssignmentResult
from datetime import datetime, timedelta

from app.schemas.question_result import QuestionResult

logger = logging.getLogger(__name__)

def get_due_user_assignments_service(user_id: str, prompt_id: int, today: datetime, db: Session):
    try:
        user_assignments = user_assignments_repository.get_user_assignments_due_by_prompt(user_id, prompt_id, today, db)
        if not user_assignments:
            return []
        return [UserAssignmentResult.from_orm(user_assignment) for user_assignment in user_assignments]
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while retrieving user assignments for user {user_id} and prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def questions_assigned_to_deck_service(deck_id: int, user_id: str, db: Session):
    try:
        user_assignments = questions_assigned_to_deck(deck_id,user_id,db)
        if not user_assignments:
            return []
        return [UserAssignmentResult.model_validate(user_assignment) for user_assignment in user_assignments]
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while retrieving user assignments for user {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def set_questions_assigned_to_deck_service(user_id:str, prompt_id: int, deck_id: int, questions: any, db: Session):
    try:
        user_assignments = assign_questions_to_user_and_deck(user_id=user_id,deck_id=deck_id,prompt_id=prompt_id,questions=questions, db=db)
        if not user_assignments:
            return []
        return user_assignments
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while retrieving user assignments for user {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def get_first_assigned_question_service(user_id: str, deck_id: int, db: Session):
    try:
        first_assigned_question = get_first_assigned_question(user_id=user_id,deck_id=deck_id, db=db)
        return UserAssignmentResult.model_validate(first_assigned_question)
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def get_user_question_assignment_service(question_assigned:int, db: Session):
    try:
        assigned_question_user = get_user_question_assignment(question_assigned, db)

        if not assigned_question_user:
            return None
        return assigned_question_user
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

def get_all_question_assignments_service(deck_id: int, db: Session):
    user_assignments = get_all_question_assignments(deck_id, db)
    if not user_assignments:
        return []
    #return [UserAssignmentResult.model_validate(user_assignment) for user_assignment in user_assignments]
    return user_assignments


def get_unassigned_questions_for_user_service(deck_id: int, db: Session):
    questions_unssigned = get_unassigned_questions_for_user(deck_id, db)
    if not questions_unssigned:
        return None
    return QuestionResult.model_validate(questions_unssigned)

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user_assignment import UserAssignment
import random


def schedule_review(assignment: UserAssignment, is_correct: bool, question_difficulty: int):
    """
    Programa la próxima revisión de una asignación basada en la corrección de la respuesta del usuario.
    
    :param assignment: La asignación de usuario a actualizar.
    :param is_correct: Indica si la respuesta fue correcta o no.
    :param question_difficulty: La dificultad fija de la pregunta (de 1 a 5).
    """
    assignment.review_count += 1

    # Ajuste de intervalo y ease_factor basado en la corrección de la respuesta
    if not is_correct:  # Again
        assignment.interval = 1
        assignment.ease_factor = max(1.3, assignment.ease_factor - 0.2)
    else:
        # La respuesta es correcta, ajustar intervalo y ease_factor
        if question_difficulty == 1:  # Hard
            assignment.interval = max(1, int(assignment.interval * 1.2))
            assignment.ease_factor = max(1.3, assignment.ease_factor - 0.15)
        elif question_difficulty == 2:  # Good
            if assignment.interval == 0:
                assignment.interval = 1
            else:
                assignment.interval = int(assignment.interval * assignment.ease_factor)
            assignment.ease_factor += 0.05
        elif question_difficulty >= 3:  # Easy
            if assignment.interval == 0:
                assignment.interval = 4
            else:
                assignment.interval = int(assignment.interval * assignment.ease_factor * 1.3)
            assignment.ease_factor += 0.15

    assignment.last_reviewed_at = datetime.utcnow()
    assignment.next_review_date = assignment.last_reviewed_at.date() + timedelta(days=assignment.interval - 1)



def calculate_user_level(user_id: str, deck_id: int, db: Session):
    """
    Calcula el nivel de conocimiento del usuario para un deck específico.
    
    :param user_id: ID del usuario
    :param deck_id: ID del deck
    :param db: Sesión de la base de datos
    :return: Un valor flotante representando el nivel del usuario (entre 0 y 1)
    """
    assignments = db.query(UserAssignment).filter(
        UserAssignment.user_id == user_id,
        UserAssignment.deck_id == deck_id
    ).all()
    
    if not assignments:
        return 0.5  # Nivel base para nuevos usuarios (mitad del rango)
    
    total_score = sum(a.ease_factor for a in assignments)
    average_score = total_score / len(assignments)
    
    # Normalizar el nivel entre 0 y 1
    return min(1, max(0, (average_score - 1.3) / 1.7))