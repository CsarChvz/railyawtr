from pydantic import BaseModel, ConfigDict, Field


class UserResponseBase(BaseModel):
    selected_option_id: int = Field(..., description="UUID of the selected option")

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 