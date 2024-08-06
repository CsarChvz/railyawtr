from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DeckBase(BaseModel):
    name: Optional[str]
    description: Optional[str]

class DeckCreate(DeckBase):
    user_id: str
    prompt_id: int

class DeckUpdate(DeckBase):
    name: Optional[str] = None
    description: Optional[str] = None

class DeckResponse(DeckBase):
    id: int
    user_id: str
    prompt_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

