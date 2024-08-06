from pydantic import ConfigDict

from .user_base import UserBase


class UserUpdateAdmin(UserBase):
    pass

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 