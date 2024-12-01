from pydantic import BaseModel


class WasteLabel(BaseModel):
    label: int
