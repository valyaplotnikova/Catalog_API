from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, List, Optional

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
    values: None = None  # Явно указываем, что значений быть не должно

    @field_validator('values')
    def validate_no_values(cls, v):
        if v is not None:
            raise ValueError("Для свойства типа 'int' не должно быть значений")
        return v


class PropertyCreate(BaseModel):
    """Объединённая модель для создания свойства с автоматическим определением типа"""
    uid: UUID = Field(default_factory=uuid4)
    name: str
    type: Literal["list", "int"]
    values: Optional[List[PropertyValueCreate]] = None

    @model_validator(mode='before')
    def validate_property_type(cls, values):
        prop_type = values.get('type')
        values_list = values.get('values', [])

        if prop_type == "list" and not values_list:
            raise ValueError("Для свойства типа 'list' необходимо указать значения")
        elif prop_type == "int" and values_list:
            raise ValueError("Для свойства типа 'int' не должно быть значений")

        return values

    class Config:
        json_encoders = {UUID: str}
