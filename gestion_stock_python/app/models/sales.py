from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        UniqueConstraint("reference", name="uq_sales_reference"),
        Index("idx_sales_created", "created_at"),
        CheckConstraint("total_amount >= 0", name="ck_sales_total"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    reference: Mapped[str] = mapped_column(String(50))
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = (
        UniqueConstraint("sale_id", "product_id", name="uq_sale_product"),
        Index("idx_sale_items_product", "product_id"),
        CheckConstraint(
            "quantity > 0 AND unit_price >= 0 AND subtotal >= 0",
            name="ck_si_qty",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    sale_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sales.id",
            name="fk_si_sale",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            name="fk_si_product",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        )
    )
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2))