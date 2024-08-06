import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.utils.auth import AuthenticationChecker, get_current_user
from app.db.database import get_db_session
from app.schemas import QuestionBase, QuestionResult
from app.schemas.question_create import QuestionCreate
from app.services import (
    create_question_from_a_prompt_service,
    delete_question_service,
    get_question_service,
    get_questions_from_a_prompt_service,
    get_random_question_service,
    update_question_service,
)

questions_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@questions_router.get(
    '/random-question',
    response_model=QuestionResult,
    status_code=201,
)
def get_random_question(db: Session = Depends(get_db_session)):
    try:
        return get_random_question_service(db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@questions_router.get(
    '/prompt/{prompt_id}',
    response_model=List[QuestionResult],
)
def get_questions_from_a_prompt(prompt_id: str, db: Session = Depends(get_db_session)):
    try:
        return get_questions_from_a_prompt_service(prompt_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@questions_router.post(
    '/prompt/{prompt_id}',
    response_model=QuestionResult,
    status_code=201,
)
def create_question_from_a_prompt(
    prompt_id: int,
    user_id: str = Query(...),
    question_data: Optional[QuestionCreate] = Depends(lambda: QuestionCreate if os.getenv('ENV') == '1' else None),
    db: Session = Depends(get_db_session),
):
    try:
        # Verificar si estamos en un entorno de pruebas
        if os.getenv('TESTING') == '1':
            current_user_id = question_data.user_id
        else:
            current_user_id = user_id

        return create_question_from_a_prompt_service(
            prompt_id, current_user_id, db
        )
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while creating question: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')


@questions_router.get(
    '/{question_id}',
    response_model=QuestionResult,
    status_code=201,
)
def get_question(
    question_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return get_question_service(question_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@questions_router.put(
    '/{question_id}',
    response_model=QuestionResult,
    status_code=201,
)
def update_question(
    question_id: int,
    question_data: QuestionBase,
    db: Session = Depends(get_db_session),
):
    try:
        return update_question_service(question_id, question_data, db)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@questions_router.delete(
    '/{question_id}',
    response_model=QuestionResult,
    status_code=201,
)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return delete_question_service(question_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
