from typing import Optional

from pydantic import ConfigDict, Field

from .prompt_base import PromptBase


class PromptCreate(PromptBase):
    response_id: Optional[int] = Field(
        None,
        description="Optional UUID of the response that triggers this prompt creation",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)