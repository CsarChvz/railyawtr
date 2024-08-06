from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, Field

from .prompt_base import PromptBase
from .question_result import QuestionResult

class PromptIndividual(PromptBase):
    id: int = Field(..., description='ID of the prompt')
    created_at: datetime = Field(..., description='Creation date of the prompt')
    user_id: Optional[str] = Field(..., description='String ID of the associated user')
    questions: List['QuestionResult'] = []
    
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
