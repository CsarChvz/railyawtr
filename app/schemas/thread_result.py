from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, Field, BaseModel

from app.schemas.prompt_base import PromptBase

from .question_thread_result import QuestionThreadResult
class ThreadResult(BaseModel):
    id: int = Field(..., description="ID of the thread")
    created_at: datetime = Field(..., description="Creation date of the prompt")
    user_id: Optional[str] = Field(..., description="String ID of the associated user")
    prompt_id: Optional[int] = Field(..., description="Integer ID of the associated prompt")
    question: QuestionThreadResult = Field(..., description="Question")
    
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
