from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.catalog import Category
from app.schemas.categories import CategoryIn


def list_categories(db: Session):
    return db.scalars(select(Category).order_by(Category.name)).all()


def update_category(db: Session, category_id: int, body: CategoryIn):
    category = db.get(Category, category_id)
    if category is None:
        raise ApiError(404, "NOT_FOUND", "Catégorie introuvable")

    category.name = body.name
    category.description = body.description

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(409, "CONFLICT", "Cette catégorie existe déjà") from exc

    db.refresh(category)
    return category


def create_category(db: Session, body: CategoryIn):
    category = Category(**body.model_dump())
    db.add(category)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(409, "CONFLICT", "Cette catégorie existe déjà") from exc

    db.refresh(category)
    return category