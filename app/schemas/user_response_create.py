from typing import Optional

from pydantic import BaseModel, Field


class UserResponseCreate(BaseModel):
    selected_option_id: int = Field(..., description='UUID of the selected option')
    user_id: Optional[str] = Field(None)