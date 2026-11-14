from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.products import ProductIn, ProductOut
from app.services import products as service

router = APIRouter(prefix="/api/products", tags=["Produits"])


@router.get("")
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    return service.list_products(db, page, limit, search, category_id)


@router.post("", status_code=201, response_model=ProductOut)
def create_product(body: ProductIn, db: Session = Depends(get_db)):
    return service.create_product(db, body)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return service.get_product(db, product_id)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    body: ProductIn,
    db: Session = Depends(get_db),
):
    return service.update_product(db, product_id, body)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    service.delete_product(db, product_id)