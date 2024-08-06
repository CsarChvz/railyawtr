import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_access import prompt_repository
from app.schemas import PromptBase, PromptUpdate

logger = logging.getLogger(__name__)


def create_prompt_service(prompt_data: PromptBase, user_id: str, db: Session):
    try:
        return prompt_repository.create_prompt(prompt_data.text, user_id, db)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while creating prompt: {e}')
        raise


def get_user_prompts_service(user_id: str, db: Session):
    try:
        return prompt_repository.get_prompts_by_user_id(user_id, db)
    except Exception as e:
        db.rollback()
        logger.error(
            f'Unexpected error while retrieving prompts for user {user_id}: {e}'
        )
        raise

def get_prompt(prompt_id: int, db: Session):
    try:
        return prompt_repository.get_prompt_by_id(prompt_id=prompt_id,db=db)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while creating prompt: {e}')
        raise

def update_prompt_service(prompt_id: str, prompt_data: PromptUpdate, db: Session):
    try:
        prompt = prompt_repository.get_prompt_by_id(prompt_id, db)
        if not prompt:
            raise HTTPException(status_code=404, detail='Prompt not found')
        return prompt_repository.update_prompt(
            prompt, prompt_data.dict(exclude_unset=True), db
        )
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while updating prompt: {e}')
        raise


def delete_prompt_service(prompt_id: str, db: Session):
    try:
        prompt = prompt_repository.get_prompt_by_id(prompt_id, db)
        if not prompt:
            raise HTTPException(status_code=404, detail='Prompt not found')
        return prompt_repository.delete_prompt(prompt, db)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while deleting prompt: {e}')
        raise

def get_all_prompts_service(db: Session):
    try:
        return prompt_repository.get_all_prompts(db)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving all prompts: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def find_prompt_by_text(text:str, db: Session):
    try:
        return prompt_repository.get_prompt_by_text(text, db)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving prompt: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')