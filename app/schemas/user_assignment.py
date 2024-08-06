from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional

from app.schemas.question_result import QuestionResult

class UserAssignmentResult(BaseModel):
    id: int
    user_id: str
    deck_id: int
    prompt_id: int
    question_id: int
    selected_option_id: Optional[int]
    created_at: datetime
    last_reviewed_at: datetime
    interval: int
    ease_factor: float
    question: QuestionResult

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
