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


class Supply(Base):
    __tablename__ = "supplies"
    __table_args__ = (
        UniqueConstraint("reference", name="uq_supplies_reference"),
        Index("idx_supplies_supplier", "supplier_id"),
        CheckConstraint("total_amount >= 0", name="ck_supplies_total"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey(
            "suppliers.id",
            name="fk_supplies_supplier",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        )
    )
    reference: Mapped[str] = mapped_column(String(50))
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


class SupplyItem(Base):
    __tablename__ = "supply_items"
    __table_args__ = (
        UniqueConstraint("supply_id", "product_id", name="uq_supply_product"),
        Index("idx_supply_items_product", "product_id"),
        CheckConstraint(
            "quantity > 0 AND unit_cost >= 0",
            name="ck_spi_qty",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    supply_id: Mapped[int] = mapped_column(
        ForeignKey(
            "supplies.id",
            name="fk_spi_supply",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            name="fk_spi_product",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        )
    )
    quantity: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        Index("idx_mov_product_date", "product_id", "created_at"),
        Index("idx_mov_reference", "reference"),
        CheckConstraint(
            "movement_type IN ('IN', 'OUT')",
            name="ck_mov_type",
        ),
        CheckConstraint("quantity > 0", name="ck_mov_qty"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            name="fk_mov_product",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        )
    )
    movement_type: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[int] = mapped_column(Integer)
    reference: Mapped[str] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )