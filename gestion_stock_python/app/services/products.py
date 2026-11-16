from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.catalog import Category, Product
from app.schemas.products import ProductIn, ProductOut


def list_products(
    db: Session,
    page: int,
    limit: int,
    search: str | None,
    category_id: int | None,
):
    query = select(Product, Category.name).join(
        Category, Category.id == Product.category_id
    )

    if search:
        query = query.where(Product.name.like(search + "%"))
    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    total = db.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar_one()

    rows = db.execute(
        query.order_by(Product.id)
        .limit(limit)
        .offset((page - 1) * limit)
    ).all()

    data = []
    for product, category_name in rows:
        values = {
            column.name: getattr(product, column.name)
            for column in Product.__table__.columns
        }
        values["category_name"] = category_name
        data.append(ProductOut.model_validate(values))

    return {
        "data": data,
        "meta": {"page": page, "limit": limit, "total": total},
    }


def get_product(db: Session, product_id: int):
    product = db.get(Product, product_id)
    if product is None:
        raise ApiError(404, "NOT_FOUND", "Produit introuvable")

    values = {
        column.name: getattr(product, column.name)
        for column in Product.__table__.columns
    }
    values["category_name"] = product.category.name
    return ProductOut.model_validate(values)
def create_product(db: Session, body: ProductIn):
    if db.get(Category, body.category_id) is None:
        raise ApiError(404, "NOT_FOUND", "Catégorie introuvable")

    product = Product(**body.model_dump())
    db.add(product)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(409, "CONFLICT", "Ce SKU existe déjà") from exc

    db.refresh(product)
    values = {
        column.name: getattr(product, column.name)
        for column in Product.__table__.columns
    }
    values["category_name"] = product.category.name
    return ProductOut.model_validate(values)


def update_product(db: Session, product_id: int, body: ProductIn):
    product = db.get(Product, product_id)
    if product is None:
        raise ApiError(404, "NOT_FOUND", "Produit introuvable")

    if db.get(Category, body.category_id) is None:
        raise ApiError(404, "NOT_FOUND", "Catégorie introuvable")

    for field, value in body.model_dump().items():
        setattr(product, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(409, "CONFLICT", "Ce SKU existe déjà") from exc

    db.refresh(product)
    values = {
        column.name: getattr(product, column.name)
        for column in Product.__table__.columns
    }
    values["category_name"] = product.category.name
    return ProductOut.model_validate(values)


def delete_product(db: Session, product_id: int):
    product = db.get(Product, product_id)
    if product is None:
        raise ApiError(404, "NOT_FOUND", "Produit introuvable")

    db.delete(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(
            409,
            "CONFLICT",
            "Ce produit est utilisé dans des ventes, approvisionnements ou mouvements.",
        ) from exc