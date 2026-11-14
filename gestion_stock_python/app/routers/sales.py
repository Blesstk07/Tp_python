from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import Page
from app.schemas.sales import SaleIn, SaleOut
from app.services import sales as service

router = APIRouter(prefix="/api/sales", tags=["Ventes"])


@router.post("", status_code=201, response_model=SaleOut)
def create_sale(body: SaleIn, db: Session = Depends(get_db)):
    return service.create_sale(db, body)


@router.get("", response_model=Page[SaleOut])
def list_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_sales(db, page, limit)


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    return service.get_sale(db, sale_id)