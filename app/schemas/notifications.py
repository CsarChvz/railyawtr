from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationBaseSchema(BaseModel):
    type_notification: str = Field(..., description='Type of the notification')
    message: str = Field(..., description='Message of the notification')
    data: Optional[Dict[str, Any]] = Field(None, description='Additional data for the notification')

class NotificationCreateSchema(NotificationBaseSchema):
    user_id: str = Field(..., description='ID of the user who receives the notification')

class NotificationResponseSchema(NotificationBaseSchema):
    id: int = Field(..., description='ID of the notification')
    user_id: str = Field(..., description='ID of the user who receives the notification')
    read: bool = Field(False, description='Whether the notification has been read')
    created_at: datetime = Field(..., description='Timestamp of the notification creation')
    updated_at: datetime = Field(..., description='Timestamp of the notification update')

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
