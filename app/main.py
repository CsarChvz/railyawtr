import os
from typing import Any, Callable

from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from dotenv import load_dotenv

# from aws_lambda_powertools.metrics import MetricUnit
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

from app.api.api import router as api_router
from app.config import get_settings
import json

from app.metadata import (
    license,
    summary,
)
from app.tags import (
    tags_metadata,
)
from app.utils.logger import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
FRONT_HOST = os.getenv("FRONT_HOST")
print("SECRETSEC_KEY")

print(SECRET_KEY)
origins = [
   FRONT_HOST
]

app = FastAPI(
    root_path=get_settings().root_path,
    title=get_settings().app_name,
    version=get_settings().version,
    summary=summary,
    description="",
    openapi_tags=tags_metadata,
    license_info=license,
    redirect_slashes=False
)
app.include_router(api_router, prefix="/api/v1")

origins = [
   FRONT_HOST, 
    "http://localhost:3000" # Reemplaza con tu origen específico
]

# Configura CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir los encabezados necesarios
    expose_headers=["*"],  # Exponer encabezados específicos
)
