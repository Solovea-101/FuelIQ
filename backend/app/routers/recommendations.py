from fastapi import APIRouter

from app.core.dependencies import DB, CurrentUser
from app.services import analytics_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
def get_recommendations(db: DB, current_user: CurrentUser):
    return analytics_service.get_recommendations(db, current_user)
