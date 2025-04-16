from uuid import UUID, uuid4

from pydantic import BaseModel, UUID4, Field
from typing import List, Optional


class PropertyValueRef(BaseModel):
    uid: UUID4
    value_uid: Optional[UUID4] = None
    value: Optional[int] = None


class ProductCreate(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    name: str
    properties: List[PropertyValueRef]


class ProductResponse(ProductCreate):
    class Config:
        from_attributes = True
        orm_mode = True
