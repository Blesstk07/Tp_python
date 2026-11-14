from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import Page
from app.schemas.suppliers import SupplierIn, SupplierOut
from app.services import suppliers as service

router = APIRouter(prefix="/api/suppliers", tags=["Fournisseurs"])


@router.get("", response_model=Page[SupplierOut])
def list_suppliers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_suppliers(db, page, limit)


@router.post("", status_code=201, response_model=SupplierOut)
def create_supplier(body: SupplierIn, db: Session = Depends(get_db)):
    return service.create_supplier(db, body)


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(
    supplier_id: int,
    body: SupplierIn,
    db: Session = Depends(get_db),
):
    return service.update_supplier(db, supplier_id, body)