from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.models.catalog import Category, Product, Supplier
from app.models.sales import Sale


def get_dashboard(db: Session):
    products_count = db.scalar(
        select(func.count()).select_from(Product)
    ) or 0
    categories_count = db.scalar(
        select(func.count()).select_from(Category)
    ) or 0
    suppliers_count = db.scalar(
        select(func.count()).select_from(Supplier)
    ) or 0
    sales_count = db.scalar(
        select(func.count()).select_from(Sale)
    ) or 0

    stock = db.execute(
        select(
            func.coalesce(func.sum(Product.quantity), 0),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Product.quantity > 0,
                                Product.quantity <= Product.min_quantity,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(case((Product.quantity == 0, 1), else_=0)),
                0,
            ),
        )
    ).one()

    return {
        "products_count": products_count,
        "categories_count": categories_count,
        "suppliers_count": suppliers_count,
        "sales_count": sales_count,
        "stock": {
            "total_quantity": stock[0],
            "low_stock_count": stock[1],
            "out_of_stock_count": stock[2],
        },
    }