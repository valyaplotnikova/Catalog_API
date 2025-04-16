from typing import Any, Optional, TypeVar, Generic, Type, List
import sqlalchemy as sa
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import ScalarResult
from database.base import Base
from uuid import UUID
import logging

# Настройка логгера
logger = logging.getLogger(__name__)
MODEL = TypeVar("MODEL", bound=Base)


class BaseCrud(Generic[MODEL]):
    """
    Базовый CRUD класс для асинхронной работы с моделями SQLAlchemy.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy

    Attributes:
        session (AsyncSession): Асинхронная сессия SQLAlchemy
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def model(self) -> Type[MODEL]:
        """Абстрактное свойство, возвращающее модель SQLAlchemy."""
        raise NotImplementedError("Должен быть определён в дочернем классе")

    async def create(self, data: dict[str, Any]) -> MODEL:
        """
        Создает новую запись в базе данных.

        Args:
            data (dict): Словарь с данными для создания записи

        Returns:
            MODEL: Созданная модель

        Raises:
            HTTPException: 400 если произошла ошибка при создании
        """
        try:
            logger.debug(f"Создание записи в {self.model.__name__} с данными: {data}")
            stmt = sa.insert(self.model).returning(self.model).values(**data)
            result = await self.session.scalar(stmt)
            await self.session.flush()

            if result is None:
                logger.error(f"Ошибка создания записи в {self.model.__name__}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create item"
                )

            logger.info(f"Успешно создана запись в {self.model.__name__} с ID: {result.uid}")
            return result

        except sa.exc.IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Ошибка целостности при создании записи: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка создания: {str(e)}"
            )

    async def get(self, uid: UUID) -> MODEL:
        """
        Получает запись по UUID.

        Args:
            uid (UUID): Идентификатор записи

        Returns:
            MODEL: Найденная модель

        Raises:
            HTTPException: 404 если запись не найдена
        """
        logger.debug(f"Получение записи {self.model.__name__} с ID: {uid}")
        stmt = sa.select(self.model).where(self.model.uid == uid)
        result: Optional[MODEL] = await self.session.scalar(stmt)

        if not result:
            logger.warning(f"Запись {self.model.__name__} с ID {uid} не найдена")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )

        logger.debug(f"Успешно найдена запись {self.model.__name__} с ID: {uid}")
        return result

    async def get_multi(
            self,
            *,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[List[sa.BinaryExpression]] = None
    ) -> List[MODEL]:
        """
        Получает список записей с пагинацией и фильтрацией.

        Args:
            skip (int): Количество записей для пропуска
            limit (int): Максимальное количество записей
            filters (List[BinaryExpression]): Список фильтров SQLAlchemy

        Returns:
            List[MODEL]: Список найденных моделей
        """
        logger.debug(f"Получение списка {self.model.__name__}, skip={skip}, limit={limit}")
        stmt = sa.select(self.model).offset(skip).limit(limit)

        if filters:
            logger.debug(f"Применение фильтров: {filters}")
            stmt = stmt.where(*filters)

        result: ScalarResult[MODEL] = await self.session.scalars(stmt)
        items = list(result.unique())
        logger.debug(f"Найдено {len(items)} записей {self.model.__name__}")
        return items

    async def update(self, uid: UUID, update_data: dict[str, Any]) -> MODEL:
        """
        Обновляет запись в базе данных.

        Args:
            uid (UUID): Идентификатор записи
            update_data (dict): Словарь с данными для обновления

        Returns:
            MODEL: Обновленная модель

        Raises:
            HTTPException: 404 если запись не найдена
        """
        logger.debug(f"Обновление записи {self.model.__name__} с ID: {uid}, данные: {update_data}")
        stmt = (
            sa.update(self.model)
            .where(self.model.uid == uid)
            .values(**update_data)
            .returning(self.model)
        )
        result: Optional[MODEL] = await self.session.scalar(stmt)

        if not result:
            logger.warning(f"Запись {self.model.__name__} с ID {uid} не найдена для обновления")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )

        await self.session.flush()
        logger.info(f"Успешно обновлена запись {self.model.__name__} с ID: {uid}")
        return result

    async def delete(self, uid: UUID) -> None:
        """
        Удаляет запись из базы данных.

        Args:
            uid (UUID): Идентификатор записи

        Raises:
            HTTPException: 404 если запись не найдена
        """
        logger.debug(f"Удаление записи {self.model.__name__} с ID: {uid}")
        stmt = sa.delete(self.model).where(self.model.uid == uid)
        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            logger.warning(f"Запись {self.model.__name__} с ID {uid} не найдена для удаления")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )

        await self.session.flush()
        logger.info(f"Успешно удалена запись {self.model.__name__} с ID: {uid}")