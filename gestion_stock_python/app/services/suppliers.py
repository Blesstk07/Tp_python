from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.catalog import Supplier
from app.schemas.suppliers import SupplierIn


def list_suppliers(db: Session, page: int, limit: int):
    total = db.scalar(select(func.count()).select_from(Supplier)) or 0
    suppliers = db.scalars(
        select(Supplier)
        .order_by(Supplier.id)
        .limit(limit)
        .offset((page - 1) * limit)
    ).all()

    return {
        "data": suppliers,
        "meta": {"page": page, "limit": limit, "total": total},
    }


def create_supplier(db: Session, body: SupplierIn):
    supplier = Supplier(**body.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(db: Session, supplier_id: int, body: SupplierIn):
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise ApiError(404, "NOT_FOUND", "Fournisseur introuvable")

    for field, value in body.model_dump().items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier