from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import DashboardOut
from app.services.dashboard import get_dashboard

router = APIRouter(prefix="/api/dashboard", tags=["Tableau de bord"])


@router.get("", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard(db)