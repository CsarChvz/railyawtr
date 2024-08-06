import datetime
import logging
from optparse import Option
import random
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_access import (
    question_repository, generate_and_save_new_questions
)
from app.models.question import Question
from app.schemas import QuestionBase
from app.services.openai_service import generate_question
from app.services import (find_prompt_by_text, 
                          generate_embeddings
                        )
logger = logging.getLogger(__name__)


def get_random_question_service(db: Session):
    questions = question_repository.get_all_questions(db)
    if not questions:
        raise HTTPException(status_code=404, detail='No questions available')
    return random.choice(questions)


def get_questions_from_a_prompt_service(prompt_id: str, db: Session):
    return question_repository.get_questions_by_prompt_id(prompt_id, db)


def create_question_from_a_prompt_service(prompt_id: str, user_id: str, prompt_settings: str, lang: str, db: Session):
    user_input = question_repository.check_prompt_exists(prompt_id, db)
    if not user_input:
        raise HTTPException(status_code=404, detail='Prompt not found')
    question_text = generate_question(prompt=prompt_settings,user_input=user_input.text, lang=lang)
    question = question_repository.create_question(prompt_id, user_id, question_text, db)
    return question



def get_question_service(question_id: int, db: Session):
    question = question_repository.get_question_by_id(question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail='Question not found')
    return question


def update_question_service(question_id: int, question_data: QuestionBase, db: Session):
    question = question_repository.get_question_by_id(question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail='Question not found')
    return question_repository.update_question(
        question, question_data.model_dump(exclude_unset=True), db
    )


def delete_question_service(question_id: int, db: Session):
    question = question_repository.get_question_by_id(question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail='Question not found')
    return question_repository.delete_question(question, db)

def find_similar_questions(db: Session, prompt: str, limit: int = 5):
    prompt_embedding = generate_embeddings(prompt)
    return (
        db.query(Question)
        .order_by(Question.embedding.cosine_distance(prompt_embedding))
        .limit(limit)
        .all()
    )

def get_existing_questions(db: Session, prompt_id: int) -> List[Question]:
    return db.query(Question).filter(Question.prompt_id == prompt_id).all()


def generate_and_save_new_questions_services(topic: str, prompt_id: int, db: Session):

    return generate_and_save_new_questions(topic=topic, prompt_id=prompt_id, db=db)