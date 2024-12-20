from pydantic import BaseModel

class CameraDelete(BaseModel):
    idCamera: int


class CameraUpdate(BaseModel):
    dataCamera: dict
