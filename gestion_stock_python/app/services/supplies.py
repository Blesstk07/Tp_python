from decimal import Decimal

from sqlalchemy import select
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