from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DB_POOL, DB_URL


engine = create_engine(
    DB_URL,
    pool_size=DB_POOL,
    max_overflow=0,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()