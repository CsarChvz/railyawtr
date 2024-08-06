
from pydantic import BaseModel

class UpdateIsSelectedSchema(BaseModel):
    is_selected: bool
