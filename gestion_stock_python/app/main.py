from fastapi import FastAPI

app = FastAPI(title="Gestion de stock (FastAPI)")


@app.get("/api/health")
def health():
    return {"status": "ok"}