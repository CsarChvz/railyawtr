import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import User
from app.schemas import UserCreate, UserUpdate, UserAuth0Base

AUTH0_DOMAIN = 'fast-api-ex.us.auth0.com'
CLIENT_ID = 'ybWKSHrlZRJbxKjmRV22734f8EbBh1Wr'
CLIENT_SECRET = 'NHilJIt9g1TTGLV2AUDgY60prhvGgUO3o9ZBfsESamtX4fSwZWEh628fM0gdCx1b'
AUDIENCE = 'https://fastapi.example.com'
SECRET_KEY = CLIENT_SECRET
ALGORITHMS = ['RS256']


async def signup(email: str, password: str, username: str):
    url = f'https://{AUTH0_DOMAIN}/dbconnections/signup'
    data = {
        'client_id': CLIENT_ID,
        'email': email,
        'password': password,
        'connection': 'Username-Password-Authentication',
        'username': username,
        'given_name': 'John',
        'family_name': 'Doe',
        'name': 'John Doe',
        'nickname': 'johnny',
        'picture': 'http://example.org/jdoe.png',
        'user_metadata': {'plan': 'silver', 'team_id': 'a111'},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()


def check_existing_user(sub_id: str, db: Session):
    return db.query(User).filter(User.id == sub_id).first()


def get_user_by_id(user_id: str, db: Session):
    return db.query(User).filter(User.id == user_id).first()


def create_user(user_data: UserCreate, db: Session) -> User:
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_user_auth0(user_data: UserAuth0Base, db: Session) -> User:
    # Convertir los datos de Pydantic a un modelo SQLAlchemy
    new_user = User(
        id=user_data.user_id or user_data.sub,
        email=user_data.email,
        password_hashed=None,
        name=user_data.name,
        username=user_data.nickname or user_data.username,
        birthday=None,
        gender=None,
        bio=None,
        profile_picture=user_data.picture,
        location=None,
        verified=user_data.email_verified,
        school_num_handles=None,
        phone_number=user_data.phone_number or None,
        providers=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Agregar y guardar el nuevo usuario en la base de datos
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(user: User, user_data: UserUpdate, db: Session) -> User:
    for key, value in user_data.dict().items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(user: User, db: Session):
    db.delete(user)
    db.commit()
