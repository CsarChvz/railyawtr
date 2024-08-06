from sqlalchemy.orm import Session
from app.models import Deck, Prompt

def get_deck_by_prompt(user_id: str, prompt_id: int, db: Session):
    return db.query(Deck).filter(Deck.user_id == user_id, Deck.prompt_id == prompt_id).first()

def create_deck(user_id: str, prompt_id:int, db:Session):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    new_deck = Deck(
        user_id=user_id,
        prompt_id=prompt_id,
        name=f'Deck of {prompt.text}'
    )
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    return new_deck


def get_deck(deck_id: int, db: Session):
    return db.query(Deck).filter(Deck.id == deck_id).first()