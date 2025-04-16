from pydantic import BaseModel
from typing import List, Union


class ProductProperty(BaseModel):
    uid: str
    name: str
    value: Union[str, int]
    value_uid: str | None = None


class ProductBase(BaseModel):
    uid: str
    name: str
    properties: List[ProductProperty]


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    pass
