from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class InvestorInterestBase(BaseModel):
    amount: float
    reason: Optional[str] = None

class InvestorInterestCreate(InvestorInterestBase):
    pass

class InvestorInterestResponse(InvestorInterestBase):
    id: int
    user_id: str
    created_at: datetime = Field(..., description="Timestamp of the notification creation")

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
