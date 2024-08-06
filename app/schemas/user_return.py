from pydantic import ConfigDict, Field

from .user_base import UserBase


class UserReturn(UserBase):
    id: str = Field(..., description="String ID of the user")
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 