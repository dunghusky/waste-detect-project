from pydantic import BaseModel


class VideoDelete(BaseModel):
    idVideo: int


class VideoUpdate(BaseModel):
    dataVideo: dict
