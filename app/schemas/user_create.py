from pydantic import ConfigDict, Field

from .user_base import UserBase


class UserCreate(UserBase):
    id: str = Field(..., description='String ID of the user', min_length=1)
    email: str = Field(..., description='Email of the user', min_length=1)
    password_hashed: str | None = Field(
        None, description='Hashed password of the user', min_length=1
    )

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 

