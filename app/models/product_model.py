import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.properties_model import Property, PropertyValue


class Product(Base):
    __tablename__ = "products"

    uid: Mapped[str] = mapped_column(primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(nullable=False)

    # Связи с таблицами свойств
    property_values: Mapped[list["ProductPropertyValue"]] = relationship(back_populates="products")
    property_ints: Mapped[list["ProductPropertyInt"]] = relationship(back_populates="products")


class ProductPropertyValue(Base):
    __tablename__ = "product_property_values"

    product_uid: Mapped[str] = mapped_column(ForeignKey("products.uid"), primary_key=True)
    property_uid: Mapped[str] = mapped_column(ForeignKey("properties.uid"), primary_key=True)
    value_uid: Mapped[str] = mapped_column(ForeignKey("property_values.uid"), nullable=False)

    # Связи с другими таблицами
    product: Mapped["Product"] = relationship(back_populates="property_values")
    property: Mapped["Property"] = relationship()
    value: Mapped["PropertyValue"] = relationship()


class ProductPropertyInt(Base):
    __tablename__ = "product_property_ints"

    product_uid: Mapped[str] = mapped_column(ForeignKey("products.uid"), primary_key=True)
    property_uid: Mapped[str] = mapped_column(ForeignKey("properties.uid"), primary_key=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False)

    # Связи с другими таблицами
    product: Mapped["Product"] = relationship(back_populates="property_ints")
    property: Mapped["Property"] = relationship()
