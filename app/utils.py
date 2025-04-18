from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs

from models.product_model import Product
from schemas.product_schema import ProductCreate, PropertyValueRef


def product_to_response(product: Product):
    properties = []

    # Обрабатываем ProductPropertyValue (list-свойства)
    for prop_value in product.property_values:
        properties.append(
            PropertyValueRef(
                uid=prop_value.property_uid, value_uid=prop_value.value_uid
            )
        )

    # Обрабатываем ProductPropertyInt (int-свойства)
    for prop_int in product.property_ints:
        properties.append(
            PropertyValueRef(property_uid=prop_int.property_uid, value=prop_int.value)
        )

    return ProductCreate.model_construct(
        uid=product.uid, name=product.name, properties=properties
    ).model_dump(exclude_none=True)


async def parse_query_params(
    query_string: str,
) -> Tuple[Dict, Dict, Optional[str], Optional[str]]:
    """
    Парсинг параметров запроса для фильтрации и поиска товаров.

    Args:
        query_string: Сырая строка запроса из request.scope["query_string"].

    Returns:
        filters: Словарь с фильтрами для свойств типа list.
        ranges: Словарь с диапазонами для свойств типа int.
        name: Имя товара для поиска (если указано).
        sort: Поле для сортировки (если указано).
    """
    parsed_query = parse_qs(query_string)
    filters = {}
    ranges = {}
    name = None
    sort = None

    for key, values in parsed_query.items():
        if key.startswith("property_"):
            if key.endswith("_from") or key.endswith("_to"):
                # Обработка диапазонов
                base_key = key.rsplit("_", 1)[0]
                if base_key not in ranges:
                    ranges[base_key] = {}
                if key.endswith("_from"):
                    ranges[base_key]["from"] = int(values[0])
                elif key.endswith("_to"):
                    ranges[base_key]["to"] = int(values[0])
            else:
                # Обработка списков значений
                filters[key] = [value for value in values]
        elif key == "name":
            name = values[0]
        elif key == "sort" and values[0] in ["name", "uid"]:
            sort = values[0]

    return filters, ranges, name, sort
