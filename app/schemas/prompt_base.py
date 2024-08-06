from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PromptBase(BaseModel):
    
    text: Optional[str] = Field(None, description='Text of the prompt')
    user_id: Optional[str] = Field(None, description='String ID of the associated user')

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 
