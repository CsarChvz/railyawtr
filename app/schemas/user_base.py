from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    name: str | None = Field(None, description='Name of the user')
    username: str | None = Field(None, description='Username of the user')
    birthday: date | None = Field(None, description='Birthday of the user')
    gender: str | None = Field(None, description='Gender of the user')
    bio: str | None = Field(None, description='Biography of the user')
    profile_picture: str | None = Field(
        None, description='Profile picture URL of the user'
    )
    location: str | None = Field(None, description='Location of the user')
    email: str | None = Field(None, description='Email of the user')
    verified: bool | None = Field(None, description='Verification status of the user')
    school_num_handles: str | None = Field(None, description='School number or handle')
    phone_number: str | None = Field(None, description='Phone number of the user')
    password_hashed: str | None = Field(None, description='Hashed password of the user')
    providers: str | None = Field(None, description='Authentication providers')
    created_at: datetime | None = Field(None, description='Creation date of the user')
    updated_at: datetime | None = Field(
        None, description='Last update date of the user'
    )
    interactions_count: int = Field(
        default=0, description='Count of user interactions with the system'
    )

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 
