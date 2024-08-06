

import logging
from fastapi import HTTPException
from pytest import Session
from app.data_access import (
    get_deck_by_prompt,
    create_deck,
    get_deck,
    get_decks_by_user_id,
    update_deck,
    delete_deck,
    get_questions_by_deck_id
)

from app.schemas import DeckResult, DeckCreateSchema, DeckUpdateSchema, QuestionResult

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
        logger.error(f"Unexpected error while retrieving deck of the prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def create_deck_service(user_id:str, prompt_id: int, db:Session):
    try:
        deck = create_deck(user_id, prompt_id, db)
        return DeckResponse.model_validate(deck)
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while retrieving deck of the prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def get_deck_service(deck_id: int, db: Session):
    try:
        deck = get_deck(deck_id, db)
        return DeckResponse.model_validate(deck)
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while retrieving deck of the prompt {deck_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



def get_decks_by_user_service(user_id: str, db: Session):
    decks = get_decks_by_user_id(user_id, db)
    return [DeckResult.model_validate(deck) for deck in decks]


def update_deck_service(deck_id: int, deck_data: DeckUpdateSchema, db: Session):
    deck = get_deck(deck_id, db)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    updated_deck = update_deck(deck, deck_data, db)
    return DeckResult.model_validate(updated_deck)

def delete_deck_service(deck_id: int, db: Session):
    deck = get_deck(deck_id, db)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    deleted_deck = delete_deck(deck, db)
    return DeckResult.model_validate(deleted_deck)

def get_questions_by_deck_service(deck_id: int, db: Session):
    assignments = get_questions_by_deck_id(deck_id, db)
    questions = [assignment.question for assignment in assignments]
    return [QuestionResult.model_validate(question) for question in questions]
