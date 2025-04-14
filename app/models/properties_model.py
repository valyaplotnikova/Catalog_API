import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from sqlalchemy import Enum as SqlAlchemyEnum, ForeignKey


class Property(Base):
    __tablename__ = "properties"

    uid: Mapped[str] = mapped_column(primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(SqlAlchemyEnum("list", "int", name="property_type"), nullable=False)

    # Связь со значениями списковых свойств
    values: Mapped[list["PropertyValue"]] = relationship(back_populates="property")


class PropertyValue(Base):
    __tablename__ = "property_values"

    uid: Mapped[str] = mapped_column(primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    property_uid: Mapped[str] = mapped_column(ForeignKey("properties.uid"), nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)

    # Связь с таблицей properties
    property: Mapped["Property"] = relationship(back_populates="values")
