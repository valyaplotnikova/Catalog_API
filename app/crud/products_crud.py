from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from models.product_model import Product, ProductPropertyValue, ProductPropertyInt
from models.properties_model import Property, PropertyValue
from schemas.product_schema import ProductCreate


class ProductCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product(self, product_uid: UUID) -> Product:
        result = await self.session.execute(
            select(Product)
            .where(Product.uid == product_uid)
            .options(
                selectinload(Product.property_values).joinedload(ProductPropertyValue.value),
                selectinload(Product.property_ints)
            )
        )
        product = result.scalars().first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Создание товара с проверкой свойств и их значений
        """
        # Проверяем существование всех свойств и их типы
        properties_info = {}
        for prop in product_data.properties:
            # Получаем информацию о свойстве
            prop_result = await self.session.execute(
                select(Property)
                .where(Property.uid == prop.uid)
            )
            db_property = prop_result.scalars().first()

            if not db_property:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property {prop.uid} does not exist"
                )

            properties_info[prop.uid] = db_property.type

            # Валидация в зависимости от типа свойства
            if db_property.type == 'list' and not prop.value_uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property {prop.uid} requires value_uid (type: list)"
                )
            elif db_property.type == 'int' and prop.value is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property {prop.uid} requires value (type: int)"
                )
            elif db_property.type == 'int' and prop.value_uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Property {prop.uid} shouldn't have value_uid (type: int)"
                )

            # Для свойств типа "list" проверяем существование value_uid
            if prop.value_uid:
                value_exists = await self.session.execute(
                    select(PropertyValue)
                    .where(PropertyValue.uid == prop.value_uid)
                    .where(PropertyValue.property_uid == prop.uid)
                )
                if not value_exists.scalars().first():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Property value {prop.value_uid} does not exist for property {prop.uid}"
                    )

        # Создаем продукт
        product = Product(name=product_data.name)
        self.session.add(product)
        await self.session.flush()

        # Добавляем свойства
        for prop in product_data.properties:
            prop_type = properties_info[prop.uid]

            if prop_type == 'list':
                prop_value = ProductPropertyValue(
                    product_uid=product.uid,
                    property_uid=prop.uid,
                    value_uid=prop.value_uid
                )
                self.session.add(prop_value)
            else:  # 'int'
                prop_int = ProductPropertyInt(
                    product_uid=product.uid,
                    property_uid=prop.uid,
                    value=prop.value
                )
                self.session.add(prop_int)

        try:
            await self.session.commit()
            await self.session.refresh(product)
            return product
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating product: {str(e)}"
            )

    async def delete_product(self, product_uid: UUID) -> None:
        product = await self.get_product(product_uid)
        await self.session.delete(product)
        await self.session.commit()
