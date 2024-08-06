
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ThreadCreate(BaseModel):
    thread_title: str
    prompt_id: int
    question_id: int
    user_id: str