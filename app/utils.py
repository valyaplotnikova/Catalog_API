from models.product_model import Product
from schemas.product_schema import ProductCreate, PropertyValueRef


def product_to_response(product: Product):
    properties = []

    # Обрабатываем ProductPropertyValue (list-свойства)
    for prop_value in product.property_values:
        properties.append(PropertyValueRef(
            uid=prop_value.property_uid,
            value_uid=prop_value.value_uid
        ))

    # Обрабатываем ProductPropertyInt (int-свойства)
    for prop_int in product.property_ints:
        properties.append(PropertyValueRef(
            property_uid=prop_int.property_uid,
            value=prop_int.value
        ))

    return ProductCreate.model_construct(
        uid=product.uid,
        name=product.name,
        properties=properties
    ).model_dump(exclude_none=True)
