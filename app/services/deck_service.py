

import logging
from fastapi import HTTPException
from pytest import Session
from app.data_access import (
    get_deck_by_prompt,
    create_deck,
    get_deck
)

from app.schemas import (DeckResponse)
logger = logging.getLogger(__name__)
def get_deck_by_prompt_service(user_id:str, prompt_id: int, db: Session):
    try:
        deck = get_deck_by_prompt(user_id=user_id, prompt_id=prompt_id, db=db)
        if deck is None:
            return None
        return DeckResponse.model_validate(deck)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving deck of the prompt {prompt_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')


def create_deck_service(user_id:str, prompt_id: int, db:Session):
    try:
        deck = create_deck(user_id, prompt_id, db)
        return DeckResponse.model_validate(deck)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving deck of the prompt {prompt_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')


def get_deck_service(deck_id: int, db: Session):
    try:
        deck = get_deck(deck_id, db)
        return DeckResponse.model_validate(deck)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving deck of the prompt {deck_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

