from pydantic import BaseModel


class ProcessWasteDelete(BaseModel):
    idVideo: int
    idWaste: int


class ProcessWasteUpdate(BaseModel):
    dataProcessWaste: dict
