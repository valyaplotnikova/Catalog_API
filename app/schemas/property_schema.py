from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Union

from uuid import UUID, uuid4


class PropertyValueCreate(BaseModel):
    value_uid: UUID = Field(default_factory=uuid4)
    value: str

    def dict(self, **kwargs):
        # Гарантируем, что UUID будет преобразован в строку
        kwargs.setdefault('by_alias', True)
        return super().dict(**kwargs)


class PropertyBase(BaseModel):
    """Базовая модель свойства"""
    uid: UUID = Field(default_factory=uuid4)
    name: str
    type: Literal["list", "int"]

    class Config:
        json_encoders = {UUID: str}


class ListPropertyCreate(PropertyBase):
    """Модель для создания свойства типа 'list'"""
    type: Literal["list"] = "list"
    values: List[PropertyValueCreate]

    @field_validator('values')
    def validate_values(cls, v):
        if not v:
            raise ValueError("Для свойства типа 'list' необходимо указать значения")
        return v


class IntPropertyCreate(PropertyBase):
    """Модель для создания свойства типа 'int'"""
    type: Literal["int"] = "int"


PropertyCreate = Union[ListPropertyCreate, IntPropertyCreate]
