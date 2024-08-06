import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import DeckResult, DeckCreateSchema, DeckUpdateSchema, QuestionResult
from app.db.database import get_db_session
from app.services import (
    get_deck_service,
    get_decks_by_user_service,
    create_deck_service,
    update_deck_service,
    delete_deck_service,
    get_questions_by_deck_service
)

decks_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@decks_router.get("/decks/", response_model=list[DeckResult])
def get_decks(user_id: str, db: Session = Depends(get_db_session)):
    try:
        return get_decks_by_user_service(user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving decks for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@decks_router.get("/decks/{deck_id}", response_model=DeckResult)
def get_deck(deck_id: int, db: Session = Depends(get_db_session)):
    try:
        return get_deck_service(deck_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving deck {deck_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@decks_router.post("/decks/", response_model=DeckResult, status_code=201)
def create_deck(deck_data: DeckCreateSchema, db: Session = Depends(get_db_session)):
    try:
        return create_deck_service(deck_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while creating deck: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@decks_router.put("/decks/{deck_id}", response_model=DeckResult)
def update_deck(deck_id: int, deck_data: DeckUpdateSchema, db: Session = Depends(get_db_session)):
    try:
        return update_deck_service(deck_id, deck_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while updating deck {deck_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@decks_router.delete("/decks/{deck_id}", response_model=DeckResult)
def delete_deck(deck_id: int, db: Session = Depends(get_db_session)):
    try:
        return delete_deck_service(deck_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while deleting deck {deck_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@decks_router.get("/decks/{deck_id}/questions", response_model=list[QuestionResult])
def get_questions_by_deck(deck_id: int, db: Session = Depends(get_db_session)):
    try:
        return get_questions_by_deck_service(deck_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving questions for deck {deck_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
