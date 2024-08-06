import logging
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_access import option_repository, get_question_by_id
from app.schemas import OptionResult, UpdateIsSelectedSchema
from app.services import generate_response_options, check_response_option

logger = logging.getLogger(__name__)


def get_options_for_question_service(question_id: int, db: Session):
    try:
        options = option_repository.get_options_by_question_id(question_id, db)
        if not options:
            return []
        return [OptionResult.from_orm(option) for option in options]
    except Exception as e:
        db.rollback()
        logger.error(
            f'Unexpected error while retrieving options for question {question_id}: {e}'
        )
        raise


def create_option_typed_for_question_service(question_id: int, option_text: str, lang: str, db: Session):
    question = get_question_by_id(question_id, db)
    is_answer_correct = check_response_option(question=question.question_text, response=option_text, lang=lang)
    new_option = option_repository.create_option(question_id=question_id, option_text=option_text, is_correct_answer=is_answer_correct, is_selected=True, is_typed=True, db=db)
    return OptionResult.from_orm(new_option)


def create_option_for_question_service(question_id: int, db: Session):
    question = get_question_by_id(question_id, db)
    options_texts = generate_response_options(question.question_text)
    new_options = []
    lineas = options_texts.split('\n')

    resultado = []

    for linea in lineas:
        # Eliminar los caracteres innecesarios y limpiar el texto
        parte_limpia = linea.split(') ')[1] if ') ' in linea else linea
        resultado.append(parte_limpia)

    resultado = [linea for linea in resultado if linea.strip()]
    print(resultado)
    
    for option_text in resultado:
        is_correct_answer = '--T--' in option_text
        clean_option_text = re.sub(r'\s*(--T--)\s*', '', option_text)
        new_option = option_repository.create_option(question_id, clean_option_text, is_correct_answer, False, False, db)
        new_options.append(new_option)
        
    return [OptionResult.from_orm(option) for option in new_options]

def update_option_service(option_id: str, option_data, db: Session):
    option = option_repository.get_option_by_id(option_id, db)
    if not option:
        raise HTTPException(status_code=404, detail='Option not found')
    return OptionResult.from_orm(
        option_repository.update_option(option, option_data, db)
    )


def delete_option_service(option_id: str, db: Session):
    option = option_repository.get_option_by_id(option_id, db)
    if not option:
        raise HTTPException(status_code=404, detail='Option not found')
    return OptionResult.from_orm(option_repository.delete_option(option, db))

def update_is_selected_service(option_id: int, update_data: UpdateIsSelectedSchema, db: Session):
    try:
        option = option_repository.update_is_selected(option_id, update_data.is_selected, db)
        if not option:
            raise HTTPException(status_code=404, detail='Option not found')
        return OptionResult.from_orm(option)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while updating is_selected for option {option_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')
    

def get_correct_option_service(question_id: str, db: Session):
    option = option_repository.get_correct_option(question_id, db)
    if not option:
        raise HTTPException(status_code=404, detail='Option not found')
    return OptionResult.model_validate(option)
