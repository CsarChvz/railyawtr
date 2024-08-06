from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, Field, BaseModel

from app.schemas.prompt_base import PromptBase
from app.schemas.prompt_result import PromptResult
from app.schemas.thread_result import ThreadResult



class Threadistory(BaseModel):
    prompt: PromptResult = Field(..., description="Prompt")
    thread: List["ThreadResult"] = Field(..., description="List of the thread")


    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)


class ThreadPromptIndividual(BaseModel):
    prompt: PromptResult = Field(..., description="Prompt")
    thread: ThreadResult= Field(..., description="Thread")


    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)