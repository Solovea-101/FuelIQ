from fastapi import APIRouter, Depends

from app.core.dependencies import DB, CurrentUser, require_role
from app.models.user import User
from app.services import driver_service

router = APIRouter(prefix="/drivers", tags=["drivers"])

ManagerOrAdmin = Depends(require_role("fleet_manager", "admin"))


@router.get("")
def list_drivers(db: DB, current_user: User = ManagerOrAdmin):
    return driver_service.list_drivers(db, current_user)


@router.get("/performance")
def get_driver_performance(db: DB, current_user: User = ManagerOrAdmin):
    return driver_service.get_driver_performance(db, current_user)


@router.get("/{driver_id}")
def get_driver(driver_id: str, db: DB, current_user: User = ManagerOrAdmin):
    return driver_service.get_driver(db, driver_id, current_user)
