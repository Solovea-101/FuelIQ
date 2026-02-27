from fastapi import APIRouter

from app.core.dependencies import DB, CurrentUser
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/fuel-efficiency")
def get_fuel_efficiency(db: DB, current_user: CurrentUser):
    return analytics_service.get_fuel_efficiency(db, current_user)


@router.get("/daily")
def get_daily_data(db: DB, current_user: CurrentUser, days: int = 14):
    return analytics_service.get_daily_data(db, current_user, days=days)


@router.get("/summary")
def get_summary(db: DB, current_user: CurrentUser):
    return analytics_service.get_summary(db, current_user)
