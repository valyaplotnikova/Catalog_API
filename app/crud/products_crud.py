from typing import Type, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import joinedload
import sqlalchemy as sa
from crud.base_crud import BaseCrud
from models.product_model import Product, ProductPropertyValue


class ProductCrud(BaseCrud[Product]):
    @property
    def model(self) -> Type[Product]:
        return Product

    async def get_with_properties(self, uid: UUID) -> Product:
        stmt = (
            sa.select(Product)
            .where(Product.uid == uid)
            .options(
                joinedload(Product.property_values).joinedload(ProductPropertyValue.value),
                joinedload(Product.property_ints)
            )
        )
        result: Optional[Product] = await self.session.scalar(stmt)
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        return result
