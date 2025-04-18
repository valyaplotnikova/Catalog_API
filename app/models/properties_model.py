from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database.base import Base
from sqlalchemy import Enum as SqlAlchemyEnum, ForeignKey


class Property(Base):
    __tablename__ = "properties"

    uid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(
        SqlAlchemyEnum("list", "int", name="property_type"), nullable=False
    )

    values: Mapped[Optional[list["PropertyValue"]]] = relationship(
        back_populates="property", cascade="all, delete-orphan", lazy="selectin"
    )


class PropertyValue(Base):
    __tablename__ = "property_values"

    uid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    property_uid: Mapped[str] = mapped_column(
        ForeignKey("properties.uid", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[str] = mapped_column(nullable=False)

    # Связь с таблицей properties
    property: Mapped["Property"] = relationship(back_populates="values")
