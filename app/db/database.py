import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Obtener la URL de la base de datos desde las variables de entorno
DEV_DATABASE_URL = os.getenv("DEV_DATABASE_URL")
if DEV_DATABASE_URL is None:
    print("IS NONE DEV--------")
    DEV_DATABASE_URL = os.getenv("DEV_DATABASE_URL")

if not DEV_DATABASE_URL:
    raise ValueError(
        "DEV_DATABASE_URL is not set. Please check your environment variables."
    )
engine = create_engine(DEV_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()

# Importar modelos
from app.models import (
    Prompt, 
    Question, 
    User, 
    Option, 
    Feedback, 
    Notification, 
    Contact, 
    InvestorInterest,
    Deck,
    UserAssignment
)

# noqa: F401


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
