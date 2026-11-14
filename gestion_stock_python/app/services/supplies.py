from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.catalog import Product, Supplier
from app.models.stock import StockMovement, Supply, SupplyItem
from app.schemas.stock import StockEntryIn, StockEntryOut
from app.utils import make_ref


def create_supply(db: Session, body: StockEntryIn):
    for attempt in range(1, 4):
        try:
            if db.get(Supplier, body.supplier_id) is None:
                raise ApiError(404, "NOT_FOUND", "Fournisseur introuvable")

            product_ids = sorted({item.product_id for item in body.items})
            products = db.execute(
                select(Product)
                .where(Product.id.in_(product_ids))
                .order_by(Product.id)
                .with_for_update()
            ).scalars().all()

            if len(products) != len(product_ids):
                raise ApiError(404, "NOT_FOUND", "Produit introuvable")

            products_by_id = {product.id: product for product in products}

            reference = make_ref("APP")
            supply = Supply(
                supplier_id=body.supplier_id,
                reference=reference,
                total_amount=Decimal("0.00"),
            )
            db.add(supply)
            db.flush()

            total = Decimal("0.00")
            for item in body.items:
                product = products_by_id[item.product_id]
                line_total = (item.unit_cost * item.quantity).quantize(
                    Decimal("0.01")
                )

                db.add(
                    SupplyItem(
                        supply_id=supply.id,
                        product_id=product.id,
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                    )
                )
                db.add(
                    StockMovement(
                        product_id=product.id,
                        movement_type="IN",
                        quantity=item.quantity,
                        reference=reference,
                    )
                )

                product.quantity += item.quantity
                total += line_total

            supply.total_amount = total
            db.commit()
            db.refresh(supply)

            return StockEntryOut.model_validate(
                {
                    "id": supply.id,
                    "reference": supply.reference,
                    "supplier_id": supply.supplier_id,
                    "total_amount": supply.total_amount,
                    "created_at": supply.created_at,
                    "items": [
                        item.model_dump() for item in body.items
                    ],
                }
            )

        except OperationalError as exc:
            db.rollback()
            original = getattr(exc, "orig", None)
            code = original.args[0] if original is not None and original.args else None

            if code in (1213, 1205) and attempt < 3:
                continue
            raise
        except Exception:
            db.rollback()
            raise


def list_stock(db: Session, page: int, limit: int, low_stock: bool):
    status = case(
        (Product.quantity == 0, "OUT"),
        (Product.quantity <= Product.min_quantity, "LOW"),
        else_="OK",
    ).label("status")

    query = select(
        Product.id.label("product_id"),
        Product.sku,
        Product.name,
        Product.quantity,
        Product.min_quantity,
        status,
    )

    if low_stock:
        query = query.where(Product.quantity <= Product.min_quantity)

    total = db.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar_one()

    rows = db.execute(
        query.order_by(Product.id)
        .limit(limit)
        .offset((page - 1) * limit)
    ).all()

    return {
        "data": [dict(row._mapping) for row in rows],
        "meta": {"page": page, "limit": limit, "total": total},
    }


def list_stock_movements(
    db: Session,
    page: int,
    limit: int,
    product_id: int | None,
    movement_type: str | None,
):
    query = select(StockMovement)

    if product_id is not None:
        query = query.where(StockMovement.product_id == product_id)
    if movement_type is not None:
        query = query.where(StockMovement.movement_type == movement_type)

    total = db.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar_one()

    rows = db.execute(
        query.order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc(),
        )
        .limit(limit)
        .offset((page - 1) * limit)
    ).scalars().all()

    data = [
        {
            column.name: getattr(movement, column.name)
            for column in StockMovement.__table__.columns
        }
        for movement in rows
    ]

    return {
        "data": data,
        "meta": {"page": page, "limit": limit, "total": total},
    }