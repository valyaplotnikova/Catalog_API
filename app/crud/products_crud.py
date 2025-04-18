import logging

from typing import List, Optional, Dict, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from models.product_model import Product, ProductPropertyValue, ProductPropertyInt
from models.properties_model import Property, PropertyValue
from schemas.catalog_schema import PropertyStats
from schemas.product_schema import ProductCreate


# Настройка логгера
logger = logging.getLogger(__name__)


class ProductCRUD:
    """CRUD операции для работы с товарами"""

    def __init__(self, session: AsyncSession):
        """Инициализация с сессией базы данных"""
        self.session = session
        logger.debug("Инициализирован ProductCRUD с сессией")

    async def get_product(self, product_uid: UUID) -> Product:
        """
        Получение товара по UUID

        Args:
            product_uid: UUID товара

        Returns:
            Product: Объект товара

        Raises:
            HTTPException: 404 если товар не найден
        """
        logger.info(f"Получение товара с UUID: {product_uid}")
        try:
            result = await self.session.execute(
                select(Product)
                .where(Product.uid == product_uid)
                .options(
                    selectinload(Product.property_values).joinedload(
                        ProductPropertyValue.value
                    ),
                    selectinload(Product.property_ints),
                )
            )
            product = result.scalars().first()

            if not product:
                logger.warning(f"Товар с UUID {product_uid} не найден")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
                )

            logger.debug(f"Успешно получен товар: {product_uid}")
            return product

        except Exception as e:
            logger.error(f"Ошибка при получении товара {product_uid}: {str(e)}")
            raise

    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Создание нового товара с валидацией свойств

        Args:
            product_data: Данные для создания товара

        Returns:
            Product: Созданный товар

        Raises:
            HTTPException: 400 при ошибках валидации
            HTTPException: 500 при ошибках базы данных
        """
        logger.info(f"Создание товара с данными: {product_data}")

        try:
            # Проверяем существование всех свойств и их типы
            properties_info = {}
            for prop in product_data.properties:
                logger.debug(f"Проверка свойства {prop.uid}")

                # Получаем информацию о свойстве
                prop_result = await self.session.execute(
                    select(Property).where(Property.uid == prop.uid)
                )
                db_property = prop_result.scalars().first()

                if not db_property:
                    logger.warning(f"Свойство {prop.uid} не найдено")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Property {prop.uid} does not exist",
                    )

                properties_info[prop.uid] = db_property.type

                # Валидация в зависимости от типа свойства
                if db_property.type == "list" and not prop.value_uid:
                    logger.warning(f"Для свойства {prop.uid} не указан value_uid")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Property {prop.uid} requires value_uid (type: list)",
                    )
                elif db_property.type == "int" and prop.value is None:
                    logger.warning(f"Для свойства {prop.uid} не указано значение")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Property {prop.uid} requires value (type: int)",
                    )
                elif db_property.type == "int" and prop.value_uid:
                    logger.warning(
                        f"Для числового свойства {prop.uid} указан value_uid"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Property {prop.uid} shouldn't have value_uid (type: int)",
                    )

                # Для свойств типа "list" проверяем существование value_uid
                if prop.value_uid:
                    value_exists = await self.session.execute(
                        select(PropertyValue)
                        .where(PropertyValue.uid == prop.value_uid)
                        .where(PropertyValue.property_uid == prop.uid)
                    )
                    if not value_exists.scalars().first():
                        logger.warning(f"Значение свойства {prop.value_uid} не найдено")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Property value {prop.value_uid} does not exist for property {prop.uid}",
                        )

            # Создаем продукт
            product = Product(name=product_data.name)
            self.session.add(product)
            await self.session.flush()
            logger.debug(f"Создан продукт с UUID: {product.uid}")

            # Добавляем свойства
            for prop in product_data.properties:
                prop_type = properties_info[prop.uid]

                if prop_type == "list":
                    prop_value = ProductPropertyValue(
                        product_uid=product.uid,
                        property_uid=prop.uid,
                        value_uid=prop.value_uid,
                    )
                    self.session.add(prop_value)
                    logger.debug(
                        f"Добавлено list-свойство: {prop.uid}={prop.value_uid}"
                    )
                else:  # 'int'
                    prop_int = ProductPropertyInt(
                        product_uid=product.uid, property_uid=prop.uid, value=prop.value
                    )
                    self.session.add(prop_int)
                    logger.debug(f"Добавлено int-свойство: {prop.uid}={prop.value}")

            await self.session.commit()
            await self.session.refresh(product)
            logger.info(f"Успешно создан товар: {product.uid}")
            return product

        except HTTPException:
            await self.session.rollback()
            raise

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при создании товара: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating product: {str(e)}",
            )

    async def delete_product(self, product_uid: UUID) -> None:
        """
        Удаление товара по UUID

        Args:
            product_uid: UUID товара для удаления

        Raises:
            HTTPException: 404 если товар не найден
            HTTPException: 500 при ошибках базы данных
        """
        logger.info(f"Удаление товара с UUID: {product_uid}")
        try:
            product = await self.get_product(product_uid)
            await self.session.delete(product)
            await self.session.commit()
            logger.info(f"Товар {product_uid} успешно удален")

        except HTTPException:
            raise

        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Ошибка при удалении товара {product_uid}: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting product: {str(e)}",
            )

    async def filter_products(
        self,
        filters: Dict[str, List[str]],
        ranges: Dict[str, Dict[str, int]],
        name: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Product], int]:
        """
        Фильтрация товаров с учетом параметров.

        Args:
            filters: Фильтры для свойств типа list.
            ranges: Диапазоны для свойств типа int.
            name: Имя товара для поиска (частичное совпадение).
            sort: Поле для сортировки ("name" или "uid").
            page: Номер страницы.
            page_size: Размер страницы.

        Returns:
            products: Список отфильтрованных товаров.
            total: Общее количество товаров, соответствующих фильтрам.
        """
        logger.info(
            f"Фильтрация товаров с параметрами: {filters}, {ranges}, {name}, {sort}"
        )

        try:
            query = select(Product).options(
                selectinload(Product.property_values).joinedload(
                    ProductPropertyValue.value
                ),
                selectinload(Product.property_ints),
            )

            # Применение фильтров
            if filters:
                for prop_uid, value_uids in filters.items():
                    query = query.join(Product.property_values).where(
                        and_(
                            ProductPropertyValue.property_uid == prop_uid,
                            ProductPropertyValue.value_uid.in_(value_uids),
                        )
                    )

            # Применение диапазонов
            if ranges:
                for prop_uid, range_values in ranges.items():
                    query = query.join(Product.property_ints).where(
                        and_(
                            ProductPropertyInt.property_uid == prop_uid,
                            ProductPropertyInt.value
                            >= range_values.get("from", float("-inf")),
                            ProductPropertyInt.value
                            <= range_values.get("to", float("inf")),
                        )
                    )

            # Поиск по имени
            if name:
                query = query.where(Product.name.ilike(f"%{name}%"))

            # Подсчет общего количества товаров
            total_query = select(func.count()).select_from(query.subquery())
            total = await self.session.execute(total_query)
            total = total.scalar()

            # Пагинация и сортировка
            if sort == "name":
                query = query.order_by(Product.name)
            elif sort == "uid":
                query = query.order_by(Product.uid)

            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await self.session.execute(query)
            products = result.scalars().all()

            logger.info(f"Найдено {len(products)} товаров из {total}")
            return products, total

        except Exception as e:
            logger.error(f"Ошибка при фильтрации товаров: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error filtering products: {str(e)}",
            )

    async def get_filter_statistics(
        self,
        filters: Dict[str, List[str]],
        ranges: Dict[str, Dict[str, int]],
    ) -> Dict[str, PropertyStats]:
        """
        Получение статистики по фильтрам.

        Args:
            filters: Фильтры для свойств типа list.
            ranges: Диапазоны для свойств типа int.

        Returns:
            Словарь с статистикой по свойствам.
        """
        query = select(Product).options(
            selectinload(Product.property_values),
            selectinload(Product.property_ints),
        )

        # Применение фильтров
        if filters:
            for prop_uid, value_uids in filters.items():
                query = query.join(Product.property_values).where(
                    and_(
                        ProductPropertyValue.property_uid == prop_uid,
                        ProductPropertyValue.value_uid.in_(value_uids),
                    )
                )

        if ranges:
            for prop_uid, range_values in ranges.items():
                query = query.join(Product.property_ints).where(
                    and_(
                        ProductPropertyInt.property_uid == prop_uid,
                        ProductPropertyInt.value
                        >= range_values.get("from", float("-inf")),
                        ProductPropertyInt.value
                        <= range_values.get("to", float("inf")),
                    )
                )

        # Подсчет общего количества товаров
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(total_query)
        total_count = total_result.scalar()

        # Сбор статистики по свойствам
        property_stats = {}

        # Статистика для свойств типа list
        for prop_uid in filters.keys():
            stats_query = (
                select(
                    ProductPropertyValue.value_uid,
                    func.count(ProductPropertyValue.value_uid),
                )
                .join(Product)
                .where(ProductPropertyValue.property_uid == prop_uid)
                .group_by(ProductPropertyValue.value_uid)
            )
            stats_result = await self.session.execute(stats_query)
            property_stats[prop_uid] = PropertyStats(
                count=total_count,
                values={uid: count for uid, count in stats_result.all()},
            )

        # Статистика для свойств типа int
        for prop_uid in ranges.keys():
            stats_query = (
                select(
                    func.min(ProductPropertyInt.value),
                    func.max(ProductPropertyInt.value),
                )
                .join(Product)
                .where(ProductPropertyInt.property_uid == prop_uid)
            )
            stats_result = await self.session.execute(stats_query)
            min_value, max_value = stats_result.one()
            property_stats[prop_uid] = PropertyStats(
                count=total_count,
                min_value=min_value,
                max_value=max_value,
            )

        return property_stats
