import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from sqlalchemy.orm import selectinload

from models.properties_model import Property, PropertyValue
from fastapi import HTTPException, status

# Настройка логгера
logger = logging.getLogger(__name__)


class PropertyCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_property(
            self,
            property_data: dict,
            values: Optional[list[dict]] = None
    ) -> Property:
        """Создание нового свойства"""

        logger.info(f"Создание записи Property с данными: {property_data}")

        try:
            if property_data['type'] == 'list' and not values:
                raise ValueError("Для свойства типа 'list' необходимо указать values")
            if property_data['type'] == 'int' and values:
                raise ValueError("Для свойства типа 'int' не должно быть values")

            db_property = Property(**property_data)

            if property_data['type'] == 'list' and values:
                db_property.values = [
                    PropertyValue(
                        uid=value_data['value_uid'],
                        value=value_data['value']
                    )
                    for value_data in values
                ]

            self.session.add(db_property)
            await self.session.commit()
            await self.session.refresh(db_property)
            logger.info(f"Успешно создана запись с ID: {db_property.uid}")
            return db_property

        except ValueError as e:
            logger.error(f"Ошибка создания записи {str(e)}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Ошибка создания записи {str(e)}")
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")

    async def get_property(self, uid: UUID) -> Property:
        """Получение свойства по UUID"""
        stmt = sa.select(Property).where(Property.uid == uid)
        result = await self.session.scalar(stmt)
        logger.info(f"Получение свойства: {uid}")
        if not result:
            logger.error(f"Cвойство: {uid} не найдено")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        return result

    async def delete_property(self, uid: UUID) -> None:
        """Удаление свойства"""
        logger.info(f"Удаление свойства: {uid}")
        stmt = sa.delete(Property).where(Property.uid == uid)
        result = await self.session.execute(stmt)
        logger.info(f"Свойство: {uid} успешно удалено")
        if result.rowcount == 0:
            logger.error(f"Cвойство: {uid} не найдено")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        await self.session.commit()

    async def get_all_properties(self) -> List[Property]:
        """Получение всех свойств с их значениями (для типа 'list')"""
        logger.info("Получение всех свойств")
        stmt = (sa.select(Property).options(selectinload(Property.values)))
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()
