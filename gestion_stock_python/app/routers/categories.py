from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.categories import CategoryIn, CategoryOut
from app.services import categories as service

router = APIRouter(prefix="/api/categories", tags=["Catégories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return service.list_categories(db)


@router.post("", status_code=201, response_model=CategoryOut)
def create_category(body: CategoryIn, db: Session = Depends(get_db)):
    return service.create_category(db, body)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    body: CategoryIn,
    db: Session = Depends(get_db),
):
    return service.update_category(db, category_id, body)