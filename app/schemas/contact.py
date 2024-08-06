from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ContactBaseSchema(BaseModel):
    follower_id: str = Field(..., description="ID of the follower")
    followed_id: str = Field(..., description="ID of the followed")

class ContactResponseSchema(ContactBaseSchema):
    id: int = Field(..., description="ID of the contact")
    created_at: datetime = Field(..., description="Timestamp when the contact was created")

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

