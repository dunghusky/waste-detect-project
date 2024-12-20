from pydantic import BaseModel


class ProcessWasteDelete(BaseModel):
    idCamera: int
    idWaste: int


class ProcessWasteUpdate(BaseModel):
    dataProcessWaste: dict
