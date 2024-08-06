from functools import lru_cache
import os

from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from pydantic import (
    Field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# Carga las variables de entorno desde el archivo .env
load_dotenv()


oauth = OAuth()
oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration",
)

# See: https://hindenes.com/testing-fastapi-basesettings
ENABLE_SETTINGS_CACHE = os.getenv("ENABLE_SETTINGS_CACHE", "TRUE").lower() == "true"


class Settings(BaseSettings):
    app_name: str = "FastAPI + Opena AI"
    version: str = "0.1.0"
    log_level: str = Field(default="INFO")
    root_path: str = Field(default="/Prod")
    aws_sam_local: bool = Field(default=False)

    def __init__(self, **data) -> None:
        super().__init__(**data)

        if self.aws_sam_local:
            self.root_path = ""


@lru_cache
def get_cached_settings() -> Settings:
    return Settings()


def get_settings() -> Settings:
    if ENABLE_SETTINGS_CACHE:
        return get_cached_settings()
    return Settings()
