

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignUpBase(BaseModel):
    username: Optional[str] = Field(None, description="Username of the user")
    email: Optional[str] = Field(None, description="Email of the user")
    password: Optional[str] = Field(None, description="Password of the user")

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 
