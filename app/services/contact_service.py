import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_access import (
    create_contact,
    delete_contact,
    get_following,
    get_followers,
    get_relationship,
    get_suggestions
)
from app.schemas.contact import ContactResponseSchema

logger = logging.getLogger(__name__)

def follow_user_service(target_user_id: str, current_user: str,db: Session):
    user_id = current_user
    if get_relationship(user_id, target_user_id, db):
        raise HTTPException(status_code=400, detail='Already following this user')
    contact = create_contact(user_id, target_user_id, db)
    return ContactResponseSchema.from_orm(contact)

def unfollow_user_service(target_user_id: str, current_user: str, db: Session):
    user_id = current_user
    contact = get_relationship(user_id, target_user_id, db)
    if not contact:
        raise HTTPException(status_code=400, detail='Not following this user')
    delete_contact(contact, db)
    return ContactResponseSchema.from_orm(contact)

def get_following_service(user_id: str, db: Session, limit: int, offset: int):
    return [ContactResponseSchema.from_orm(contact) for contact in get_following(user_id, db, limit, offset)]

def get_followers_service(user_id: str, db: Session, limit: int, offset: int):
    return [ContactResponseSchema.from_orm(contact) for contact in get_followers(user_id, db, limit, offset)]

def get_relationship_service(user_id: str, target_user_id: str, db: Session):
    contact = get_relationship(user_id, target_user_id, db)
    if not contact:
        raise HTTPException(status_code=404, detail='Relationship not found')
    return ContactResponseSchema.from_orm(contact)

def get_suggestions_service(user_id: str, db: Session):
    suggestions = get_suggestions(user_id, db)
    return [ContactResponseSchema.from_orm(user) for user in suggestions]
