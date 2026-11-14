from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.catalog import Product
from app.models.sales import Sale, SaleItem
from app.models.stock import StockMovement
from app.schemas.sales import SaleIn, SaleOut
from app.utils import make_ref


def create_sale(db: Session, body: SaleIn):
    for attempt in range(1, 4):
        try:
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
            insufficient = [
                {
                    "product_id": item.product_id,
                    "requested": item.quantity,
                    "available": products_by_id[item.product_id].quantity,
                }
                for item in body.items
                if products_by_id[item.product_id].quantity < item.quantity
            ]
            if insufficient:
                raise ApiError(
                    409,
                    "INSUFFICIENT_STOCK",
                    "Stock insuffisant",
                    insufficient,
                )

            reference = make_ref("VTE")
            sale = Sale(reference=reference, total_amount=Decimal("0.00"))
            db.add(sale)
            db.flush()

            total = Decimal("0.00")
            response_items = []

            for item in body.items:
                product = products_by_id[item.product_id]
                subtotal = (product.sale_price * item.quantity).quantize(
                    Decimal("0.01")
                )

                db.add(
                    SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=item.quantity,
                        unit_price=product.sale_price,
                        subtotal=subtotal,
                    )
                )
                db.add(
                    StockMovement(
                        product_id=product.id,
                        movement_type="OUT",
                        quantity=item.quantity,
                        reference=reference,
                    )
                )

                product.quantity -= item.quantity
                total += subtotal
                response_items.append(
                    {
                        "product_id": product.id,
                        "product_name": product.name,
                        "quantity": item.quantity,
                        "unit_price": product.sale_price,
                        "subtotal": subtotal,
                    }
                )

            sale.total_amount = total
            db.commit()
            db.refresh(sale)

            return SaleOut.model_validate(
                {
                    "id": sale.id,
                    "reference": sale.reference,
                    "total_amount": sale.total_amount,
                    "created_at": sale.created_at,
                    "items": response_items,
                }
            )

        except OperationalError as exc:
            db.rollback()
            original = getattr(exc, "orig", None)
            code = (
                original.args[0]
                if original is not None and original.args
                else None
            )
            if code in (1213, 1205) and attempt < 3:
                continue
            raise
        except Exception:
            db.rollback()
            raise


def _sales_with_items(db: Session, sales: list[Sale]):
    if not sales:
        return []

    sale_ids = [sale.id for sale in sales]
    rows = db.execute(
        select(SaleItem, Product.name)
        .join(Product, Product.id == SaleItem.product_id)
        .where(SaleItem.sale_id.in_(sale_ids))
        .order_by(SaleItem.sale_id, SaleItem.id)
    ).all()

    items_by_sale: dict[int, list[dict]] = {sale_id: [] for sale_id in sale_ids}
    for item, product_name in rows:
        items_by_sale[item.sale_id].append(
            {
                "product_id": item.product_id,
                "product_name": product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal,
            }
        )

    return [
        SaleOut.model_validate(
            {
                "id": sale.id,
                "reference": sale.reference,
                "total_amount": sale.total_amount,
                "created_at": sale.created_at,
                "items": items_by_sale[sale.id],
            }
        )
        for sale in sales
    ]


def list_sales(db: Session, page: int, limit: int):
    total = db.scalar(select(func.count()).select_from(Sale)) or 0
    sales = db.scalars(
        select(Sale)
        .order_by(Sale.created_at.desc(), Sale.id.desc())
        .limit(limit)
        .offset((page - 1) * limit)
    ).all()

    return {
        "data": _sales_with_items(db, sales),
        "meta": {"page": page, "limit": limit, "total": total},
    }


def get_sale(db: Session, sale_id: int):
    sale = db.get(Sale, sale_id)
    if sale is None:
        raise ApiError(404, "NOT_FOUND", "Vente introuvable")

    return _sales_with_items(db, [sale])[0]