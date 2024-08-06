from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class FeedbackBaseSchema(BaseModel):
    message: str = Field(..., description='Message of the feedback')

class FeedbackCreateSchema(FeedbackBaseSchema):
    pass 
class FeedbackResponseSchema(FeedbackBaseSchema):
    id: int = Field(..., description='ID of the feedback')
    timestamp: datetime = Field(..., description='Timestamp of the feedback')
    user_id: str = Field(..., description='ID of the user who provided the feedback')

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

