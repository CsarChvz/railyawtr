from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserUpdate(BaseModel):
    name: str | None = Field(None, description="Name of the user")
    username: str | None = Field(None, description="Username of the user")
    birthday: datetime | None = Field(None, description="Birthday of the user")
    gender: str | None = Field(None, description="Gender of the user")
    bio: str | None = Field(None, description="Biography of the user")
    profile_picture: str | None = Field(
        None, description="Profile picture URL of the user"
    )
    location: str | None = Field(None, description="Location of the user")
    school_num_handles: str | None = Field(None, description="School number or handle")
    phone_number: str | None = Field(None, description="Phone number of the user")

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 

