from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from .prompt_base import PromptBase


class PromptResult(PromptBase):
    id: int = Field(..., description='ID of the prompt')
    created_at: datetime = Field(..., description='Creation date of the prompt')
    user_id: Optional[str] = Field(..., description='String ID of the associated user')

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
