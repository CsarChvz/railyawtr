from sqlalchemy.orm import Session
from app.models import Prompt

def create_prompt(text: str, user_id: str, db: Session):
    new_prompt = Prompt(text=text, user_id=user_id)
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return new_prompt


def create_prompt_emb(text: str, user_id: str, embedding: any, db: Session):
    new_prompt = Prompt(text=text, user_id=user_id, embedding=embedding)
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return new_prompt

def find_similar_prompts(query_embedding, db: Session):
    k = 2
    similarity_threshold = 0.98
    query = db.query(Prompt, Prompt.embedding.cosine_distance(query_embedding)
            .label("distance")).filter(Prompt.embedding.cosine_distance(query_embedding) < similarity_threshold).order_by("distance").limit(k).all()
    
    return query


def get_prompts_by_user_id(user_id: str, db: Session):
    return db.query(Prompt).filter(Prompt.user_id == user_id).all()

def get_prompt_by_id(prompt_id: str, db: Session):
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()

def update_prompt(prompt, prompt_data, db: Session):
    for key, value in prompt_data.items():
        if value is not None:
            setattr(prompt, key, value)
    db.commit()
    db.refresh(prompt)
    return prompt

def delete_prompt(prompt, db: Session):
    db.delete(prompt)
    db.commit()
    return prompt

def get_all_prompts(db: Session):
    return db.query(Prompt).all()


def get_prompt_by_text(text:str, db: Session):
    return db.query(Prompt).filter(Prompt.text == text).first()