from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from crud.properties_crud import PropertyCRUD
from database.database import db_helper
from schemas.property_schema import ListPropertyCreate, IntPropertyCreate

router = APIRouter()


@router.post("/properties/")
async def add_property(property_data: Union[ListPropertyCreate, IntPropertyCreate],
                       session: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    """Создание нового свойства"""
    crud = PropertyCRUD(session)

    try:
        if isinstance(property_data, ListPropertyCreate):
            values = [v.dict(by_alias=True) for v in property_data.values]
            return await crud.create_property(
                property_data.dict(exclude={"values"}),
                values
            )
        else:
            return await crud.create_property(
                property_data.dict(),
                None
            )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/properties/{uid}")
async def delete_property(uid: UUID, session: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    """Удаление свойства"""
    crud = PropertyCRUD(session)
    try:
        await crud.delete_property(uid)
        return {"response": "property delete"}
    except HTTPException as e:
        raise e
