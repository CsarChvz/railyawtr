from typing import List
from pydantic import BaseModel, ConfigDict
from app.schemas.option_result import OptionResult
from app.schemas.prompt_result import PromptResult
from app.schemas.question_result import QuestionResult

class FlowResult(BaseModel):
    prompt: PromptResult
    question: QuestionResult
    options: List[OptionResult]

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
