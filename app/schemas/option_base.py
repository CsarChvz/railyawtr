from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class OptionBase(BaseModel):
    option_text: Optional[str] = Field(None, description='Text of the option')

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 