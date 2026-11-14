from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import products, categories, suppliers, stock, sales, dashboard
from app.core.errors import register_error_handlers
 
app = FastAPI(title="Gestion de stock (FastAPI)", version="1.0")
@app.get("/api/health")
def health(): return {"status": "ok"}
for r in (products, categories, suppliers, stock, sales, dashboard):
    app.include_router(r.router)
register_error_handlers(app)
app.mount("/app", StaticFiles(directory="static", html=True), name="app")