from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud.products_crud import ProductCRUD
from database.database import db_helper
from schemas.product_schema import ProductCreate, ProductResponse

router = APIRouter()


@router.get("/product/{uid}")
async def get_product(session: Annotated[AsyncSession, Depends(db_helper.session_getter)], product_uid: UUID):
    crud = ProductCRUD(session)
    product = await crud.get_product(product_uid)
    return ProductResponse.from_orm(product)


@router.post("/product/")
async def add_product(product_data: ProductCreate, session: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    crud = ProductCRUD(session)
    product = await crud.create_product(product_data)
    return product


@router.delete("/product/{uid}")
async def delete_product(session: Annotated[AsyncSession, Depends(db_helper.session_getter)], product_uid: UUID):
    crud = ProductCRUD(session)
    try:
        await crud.delete_product(product_uid)
        return {"response": "product delete"}
    except HTTPException as e:
        raise e
