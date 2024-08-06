from pydantic import ConfigDict

from .prompt_base import PromptBase


class PromptUpdate(PromptBase):
    pass

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True) 
