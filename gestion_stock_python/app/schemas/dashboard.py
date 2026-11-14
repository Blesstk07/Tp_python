from pydantic import BaseModel


class StockSummary(BaseModel):
    total_quantity: int
    low_stock_count: int
    out_of_stock_count: int


class DashboardOut(BaseModel):
    products_count: int
    categories_count: int
    suppliers_count: int
    sales_count: int
    stock: StockSummary