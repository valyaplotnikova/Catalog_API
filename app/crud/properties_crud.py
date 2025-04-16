import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
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

        logger.debug(f"Создание записи Property с данными: {property_data}")

        try:
            # Создаем основное свойство
            db_property = Property(**property_data)
            self.session.add(db_property)

            # Если тип 'list', добавляем значения
            if property_data['type'] == 'list' and values:
                for value_data in values:
                    db_value = PropertyValue(
                        uid=value_data['value_uid'],
                        property_uid=db_property.uid,
                        value=value_data['value']
                    )
                    self.session.add(db_value)

            await self.session.commit()
            await self.session.refresh(db_property)
            logger.info(f"Успешно создана запись с ID: {db_property.uid}")
            return db_property

        except Exception as e:
            logger.error(f"Ошибка создания записи {str(e)}")
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")

    async def get_property(self, uid: UUID) -> Property:
        """Получение свойства по UUID"""
        stmt = sa.select(Property).where(Property.uid == uid)
        result = await self.session.scalar(stmt)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        return result

    async def delete_property(self, uid: UUID) -> None:
        """Удаление свойства"""
        stmt = sa.delete(Property).where(Property.uid == uid)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        await self.session.commit()
