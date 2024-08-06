from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, AnyHttpUrl, ConfigDict


class UserAuth0Base(BaseModel):
    app_metadata: Optional[dict] = Field(None, description='Application-specific metadata')
    created_at: Optional[datetime] = Field(None, description='Creation date of the user')
    email: Optional[str] = Field(None, description='Email of the user')
    email_verified: Optional[bool] = Field(None, description='Whether the email has been verified')
    family_name: Optional[str] = Field(None, description='Family name of the user')
    given_name: Optional[str] = Field(None, description='Given name of the user')
    last_password_reset: Optional[datetime] = Field(None, description='Last password reset date')
    name: Optional[str] = Field(None, description='Full name of the user')
    nickname: Optional[str] = Field(None, description='Nickname of the user')
    phone_number: Optional[str] = Field(None, description='Phone number of the user')
    picture: Optional[str] = Field(None, description='Profile picture URL of the user')
    tenant: Optional[str] = Field(None, description='Auth0 tenant')
    updated_at: Optional[datetime] = Field(None, description='Last update date of the user')
    user_id: Optional[str] = Field(None, description='Unique identifier for the user')
    user_metadata: Optional[dict] = Field(None, description='User-specific metadata')
    username: Optional[str] = Field(None, description='Username of the user')
    sub: Optional[str] = Field(None, description='Unique identifier for the user [sub]')

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
