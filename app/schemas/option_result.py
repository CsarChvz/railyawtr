
from pydantic import Field , ConfigDict

from .option_base import OptionBase


class OptionResult(OptionBase):
    id: int = Field(..., description="ID of the option")
    question_id: int = Field(..., description="ID of the associated question")
    is_correct_answer: bool = Field(..., description="ID of the associated question")
    is_selected: bool = Field(..., description="ID of the associated question")
    is_typed: bool = Field(False, description="Boolean if is typed option")
    
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 
