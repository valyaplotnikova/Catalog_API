import logging
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class RunConfig(BaseModel):
    """
    Конфигурация параметров запуска приложения.

    Attributes:
        host (str): Хост для запуска сервера (по умолчанию '0.0.0.0')
        port (int): Порт для запуска сервера (по умолчанию 8000)
    """
    host: str = "0.0.0.0"
    port: int = 8000


class LoggingConfig(BaseModel):
    """
    Конфигурация логирования приложения.

    Attributes:
        log_level (Literal): Уровень логирования (debug, info, warning, error, critical)
        log_format (str): Формат логов
    """
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT

    @property
    def log_level_value(self) -> int:
        """Возвращает числовое значение уровня логирования."""
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class DatabaseConfig(BaseModel):
    """
    Конфигурация подключения к базе данных.

    Attributes:
        url (PostgresDsn): URL подключения к БД
        echo (bool): Логирование SQL запросов
        echo_pool (bool): Логирование пула соединений
        pool_size (int): Размер пула соединений
        max_overflow (int): Максимальное переполнение пула
        naming_convention (dict): Конвенции именования для SQLAlchemy
    """
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    """
    Основные настройки приложения.

    Загружает конфигурацию из .env файла с префиксом APP_CONFIG__.
    """
    model_config = SettingsConfigDict(
        env_file=(".env",),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    logging: LoggingConfig = LoggingConfig()
    db: DatabaseConfig


def configure_logging(log_config: LoggingConfig):
    """
    Настраивает глобальное логирование для приложения.

    Args:
        log_config (LoggingConfig): Конфигурация логирования
    """
    logging.basicConfig(
        level=log_config.log_level_value,
        format=log_config.log_format,
    )
    logger = logging.getLogger(__name__)
    logger.info("Логирование успешно настроено")


# Инициализация настроек и логирования
settings = Settings()
configure_logging(settings.logging)
