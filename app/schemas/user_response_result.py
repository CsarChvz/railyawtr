from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from .user_response_base import UserResponseBase


class UserResponseResult(UserResponseBase):
    id: int = Field(..., description='UUID of the user response')
    question_id: int = Field(..., description='UUID of the associated question')
    user_id: str = Field(..., description='String ID of the associated user')
    selected_option_id: int = Field(..., description='UUID of the selected option')
    created_at: Optional[datetime] = Field(
        None, description='Creation date of the user response'
    )

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 