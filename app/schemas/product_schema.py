from uuid import UUID, uuid4

from pydantic import BaseModel, UUID4, Field, ConfigDict
from typing import List, Optional


class PropertyValueRef(BaseModel):
    uid: UUID4
    value_uid: Optional[UUID4] = None
    value: Optional[int] = None


class ProductCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID = Field(default_factory=uuid4)
    name: str
    properties: List[PropertyValueRef]
