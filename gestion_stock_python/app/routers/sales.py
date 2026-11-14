from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.sales import SaleIn, SaleOut
from app.services import sales as service

router = APIRouter(prefix="/api/sales", tags=["Ventes"])


@router.post("", status_code=201, response_model=SaleOut)
def create_sale(body: SaleIn, db: Session = Depends(get_db)):
    return service.create_sale(db, body)