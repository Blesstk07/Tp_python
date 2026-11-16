import os

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault(
    "DB_URL",
    "mysql+pymysql://test:test@127.0.0.1:3307/gestion_stock_python?charset=utf8mb4",
)
os.environ.setdefault("DB_POOL", "10")

from app.main import app


EXPECTED_ROUTES = {
    "/api/health": {"get"},
    "/api/products": {"get", "post"},
    "/api/products/{product_id}": {"get", "put", "delete"},
    "/api/categories": {"get", "post"},
    "/api/categories/{category_id}": {"put"},
    "/api/suppliers": {"get", "post"},
    "/api/suppliers/{supplier_id}": {"put"},
    "/api/stock": {"get"},
    "/api/stock/entries": {"post"},
    "/api/stock/movements": {"get"},
    "/api/sales": {"get", "post"},
    "/api/sales/{sale_id}": {"get"},
    "/api/dashboard": {"get"},
}


def test_openapi_contains_all_contract_routes():
    paths = app.openapi()["paths"]

    for path, methods in EXPECTED_ROUTES.items():
        assert path in paths
        assert methods <= paths[path].keys()
