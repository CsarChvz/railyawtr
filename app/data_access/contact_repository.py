from sqlalchemy.orm import Session
from app.models import Contact, User

def create_contact(follower_id: str, followed_id: str, db: Session):
    new_contact = Contact(follower_id=follower_id, followed_id=followed_id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def delete_contact(contact: Contact, db: Session):
    db.delete(contact)
    db.commit()
    return contact

def get_following(user_id: str, db: Session, limit: int, offset: int):
    return db.query(Contact).filter(Contact.follower_id == user_id).limit(limit).offset(offset).all()

def get_followers(user_id: str, db: Session, limit: int, offset: int):
    return db.query(Contact).filter(Contact.followed_id == user_id).limit(limit).offset(offset).all()

def get_relationship(user_id: str, target_user_id: str, db: Session):
    return db.query(Contact).filter(Contact.follower_id == user_id, Contact.followed_id == target_user_id).first()

def get_suggestions(user_id: str, db: Session):
    #sugerencias de usuarios a seguir...

    
    subquery = db.query(Contact.followed_id).filter(Contact.follower_id == user_id).subquery()
    return db.query(User).filter(User.id != user_id, ~User.id.in_(subquery)).all()
