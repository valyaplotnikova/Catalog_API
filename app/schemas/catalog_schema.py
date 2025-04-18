from pydantic import BaseModel
from typing import List, Optional, Dict, Union


class PropertyValueOut(BaseModel):
    uid: str
    name: str
    value_uid: Optional[str] = None
    value: Union[str, int, float]


class ProductOut(BaseModel):
    uid: str
    name: str
    properties: List[PropertyValueOut]


class CatalogResponse(BaseModel):
    products: List[ProductOut]
    count: int


class FilterValueCount(BaseModel):
    count: int


class NumericFilterRange(BaseModel):
    min_value: Union[int, float]
    max_value: Union[int, float]


class FilterResponse(BaseModel):
    count: int
    properties: Dict[str, Dict[str, FilterValueCount]]
    numeric_properties: Dict[str, NumericFilterRange]


class PropertyStats(BaseModel):
    count: int
    values: Optional[Dict[str, int]] = None  # Для свойств типа list
    min_value: Optional[int] = None  # Для свойств типа int
    max_value: Optional[int] = None  # Для свойств типа int


class CatalogFilterResponse(BaseModel):
    count: int
    properties: Dict[str, PropertyStats]
