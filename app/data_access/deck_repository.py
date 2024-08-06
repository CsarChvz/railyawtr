from sqlalchemy.orm import Session
from app.models import Deck, Prompt, UserAssignment

def get_deck_by_prompt(user_id: str, prompt_id: int, db: Session):
    return db.query(Deck).filter(Deck.user_id == user_id, Deck.prompt_id == prompt_id).first()

def create_deck(user_id: str, prompt_id:int, db:Session):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    new_deck = Deck(
        user_id=user_id,
        prompt_id=prompt_id,
        name=f"Deck of {prompt.text}"
    )
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    return new_deck


def get_deck(deck_id: int, db: Session):
    return db.query(Deck).filter(Deck.id == deck_id).first()

def get_decks_by_user_id(user_id: str, db: Session):
    return db.query(Deck).filter(Deck.user_id == user_id).all()

def update_deck(deck, deck_data, db: Session):
    for key, value in deck_data.dict(exclude_unset=True).items():
        setattr(deck, key, value)
    db.commit()
    db.refresh(deck)
    return deck

def delete_deck(deck, db: Session):
    db.delete(deck)
    db.commit()
    return deck

def get_questions_by_deck_id(deck_id: int, db: Session):
    return db.query(UserAssignment).filter(UserAssignment.deck_id == deck_id).all()
