from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common import Page
from app.schemas.stock import (
    StockEntryIn,
    StockEntryOut,
    StockLevelOut,
    StockMovementOut,
)
from app.services import supplies as service

router = APIRouter(prefix="/api/stock", tags=["Stock"])


@router.get("", response_model=Page[StockLevelOut])
def list_stock(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    low_stock: bool = Query(False),
    db: Session = Depends(get_db),
):
    return service.list_stock(db, page, limit, low_stock)


@router.post("/entries", status_code=201, response_model=StockEntryOut)
def create_stock_entry(
    body: StockEntryIn,
    db: Session = Depends(get_db),
):
    return service.create_supply(db, body)


@router.get("/movements", response_model=Page[StockMovementOut])
def list_stock_movements(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    product_id: int | None = Query(None, gt=0),
    movement_type: Literal["IN", "OUT"] | None = Query(None, alias="type"),
    db: Session = Depends(get_db),
):
    return service.list_stock_movements(
        db, page, limit, product_id, movement_type
    )