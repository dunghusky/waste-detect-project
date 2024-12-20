from pydantic import BaseModel


class CategoryModelDelete(BaseModel):
    idModel: int


class CategoryModelUpdate(BaseModel):
    dataCategoryModel: dict
