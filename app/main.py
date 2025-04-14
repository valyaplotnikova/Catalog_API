import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, APIRouter


from core.config import settings


logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    """Управление жизненным циклом приложения."""
    logging.info("Инициализация приложения...")
    yield
    logging.info("Завершение работы приложения...")


def create_app() -> FastAPI:
    """
   Создание и конфигурация FastAPI приложения.

   Returns:
       Сконфигурированное приложение FastAPI
   """
    app = FastAPI(
        title="Catalog-API",
        lifespan=lifespan,
    )

    # Регистрация роутеров
    register_routers(app)

    return app


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""
    # Корневой роутер
    root_router = APIRouter()

    @root_router.get("/", tags=["root"])
    def home_page():
        return {
            "message": "Добро пожаловать!",
        }

    # Подключение роутеров
    app.include_router(root_router, tags=["root"])


# Создание экземпляра приложения
app = create_app()
