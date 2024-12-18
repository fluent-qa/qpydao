from __future__ import annotations

from abc import ABCMeta
from typing import Any

from pydantic import BaseModel, model_validator
from qpyconf import settings
from sqlmodel import Field, SQLModel

from .exceptions import DatabaseClientConfigError


def _validate_param(name: str, value: str) -> None:
    if not value:
        raise DatabaseClientConfigError(
            f'Database parameter "{name}" is not set or empty and is required'
        )


class DatabaseConfig(BaseModel):
    """database client configurations."""

    db_url: str | None = None
    host: str = None
    user: str = None
    password: str = None
    database: str = None
    port: int | None = 5432
    pool_size: int | None = 10
    pool_recycle: int | None = 3600
    echo_queries: bool | None = True
    charset: str | None = "utf8"
    options: dict[str, Any] = None

    @model_validator(mode="after")
    def check_db_url(self):
        if self.db_url is None:
            _validate_param("host", self.host)
            _validate_param("user", self.host)
            _validate_param("password", self.host)
            _validate_param("port", self.host)
            _validate_param("database", self.host)

class SqlRequestModel(BaseModel):
    """SqlRequestModel: Model for SQLRequest."""

    config: DatabaseConfig
    sql: str
    parameters: dict = {}
    db_name: str


class FieldMeta(BaseModel):
    """Field Meta: Model for Field."""

    field_name: str
    field_type: str
    code_type: str = ""
    code_value: str = ""


class TableMeta(BaseModel):
    """TableMeta: Model for Table."""

    table_name: str
    fields: list[FieldMeta]


class BaseEntity(SQLModel):
    """BaseEntity: Model for BaseEntity."""

    pass


class BaseIDModel(BaseEntity):
    id: int | None = Field(default=None, primary_key=True)


def database_config(db_name: str = "default") -> DatabaseConfig:
    return DatabaseConfig(**settings.databases[db_name])


class SingletonMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
