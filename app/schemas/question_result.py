from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from .question_base import QuestionBase


class QuestionResult(QuestionBase):
    id: int = Field(..., description="ID of the question")
    prompt_id: int = Field(..., description="ID of the associated prompt")
    created_at: Optional[datetime] = Field(None, description="Creation date of the question")
    difficulty: int

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 