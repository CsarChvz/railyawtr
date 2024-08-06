from sqlalchemy.orm import Session
from app.models import Option, Question

def get_options_by_question_id(question_id: int, db: Session):
    return db.query(Option).filter(Option.question_id == question_id).all()

def create_option(question_id: int, option_text: str, is_correct_answer: bool, is_selected:bool, is_typed:bool, db: Session):
    new_option = Option(question_id=question_id, option_text=option_text, is_correct_answer=is_correct_answer, is_selected=is_selected, is_typed=is_typed)
    db.add(new_option)
    db.commit()
    db.refresh(new_option)
    return new_option


def update_option(option, option_data, db: Session):
    for key, value in option_data.dict(exclude_unset=True).items():
        setattr(option, key, value)
    db.commit()
    db.refresh(option)
    return option

def delete_option(option, db: Session):
    db.delete(option)
    db.commit()
    return option

def get_option_by_id(option_id: str, db: Session):
    return db.query(Option).filter(Option.id == option_id).first()

def get_question_by_id(question_id: int, db: Session):
    return db.query(Question).filter(Question.id == question_id).first()


def update_is_selected(option_id: int, is_selected: bool, db: Session):
    option = get_option_by_id(option_id, db)
    if not option:
        return None
    option.is_selected = is_selected
    db.commit()
    db.refresh(option)
    return option

def get_correct_option(question_id: int, db: Session) -> Option:
    correct_option = (
        db.query(Option)
        .filter(Option.question_id == question_id, Option.is_correct_answer == True)
        .first()
    )
    return correct_option