import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_access import user_repository
from app.schemas import UserCreate, UserReturn, UserUpdate, UserAuth0Base

logger = logging.getLogger(__name__)


async def create_user_service(user_data: UserCreate, db: Session) -> UserReturn:
    # Register user with Auth0
    try:
        await user_repository.signup(
            user_data.email, user_data.password_hashed, user_data.name
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f'Unexpected error during signup: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

    # Check if user already exists
    existing_user = user_repository.check_existing_user(user_data.id, db)
    if existing_user:
        raise HTTPException(status_code=400, detail='User already exists with this id')

    # Create new user
    try:
        new_user = user_repository.create_user(user_data, db)
        return UserReturn.from_orm(new_user)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while creating user: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

async def create_user_auth0(user_data: UserAuth0Base, db: Session)-> UserReturn:
    # Check if user already exists
    existing_user = user_repository.check_existing_user(user_data.user_id or user_data.sub, db)
    if existing_user:
        #raise HTTPException(status_code=400, detail='User already exists with this id')
        return UserReturn.from_orm(existing_user)
    else:
        # Create new user
        try:
            new_user = user_repository.create_user_auth0(user_data, db)
            return UserReturn.from_orm(new_user)
        except Exception as e:
            db.rollback()
            logger.error(f'Unexpected error while creating user: {e}')
            raise HTTPException(status_code=500, detail='Internal server error')


def get_user_service(user_id: str, db: Session) -> UserReturn:
    user = user_repository.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return UserReturn.from_orm(user)


def update_user_service(user_id: str, user_data: UserUpdate, db: Session) -> UserReturn:
    user = user_repository.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    updated_user = user_repository.update_user(user, user_data, db)
    return UserReturn.from_orm(updated_user)


def delete_user_service(user_id: str, db: Session) -> str:
    user = user_repository.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    user_repository.delete_user(user, db)
    return 'User deleted successfully'
