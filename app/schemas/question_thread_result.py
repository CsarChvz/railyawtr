from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .question_base import QuestionBase
from .option_result import OptionResult

class QuestionThreadResult(BaseModel):
    id: int = Field(..., description='ID of the question')
    question_text: Optional[str] = Field(None, description='Text of the question')
    options: List['OptionResult'] = []
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 