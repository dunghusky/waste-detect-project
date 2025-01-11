from typing import Union
from fastapi import UploadFile
from pydantic import BaseModel


class WasteDelete(BaseModel):
    idWaste: int


class WasteUpdate(BaseModel):
    dataWaste: dict


