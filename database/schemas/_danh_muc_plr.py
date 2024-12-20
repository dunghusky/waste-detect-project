from pydantic import BaseModel


class CategoryWasteDelete(BaseModel):
    idWasteCategory: int


class CategoryWasteUpdate(BaseModel):
    dataCategoryWaste: dict
