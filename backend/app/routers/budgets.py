from fastapi import APIRouter, Depends, status

from app.core.dependencies import DB, require_role
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate
from app.services import budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])

ManagerOrAdmin = Depends(require_role("fleet_manager", "admin"))


@router.get("")
def list_budgets(db: DB, current_user: User = ManagerOrAdmin):
    return budget_service.list_budgets(db, current_user)


@router.get("/{route_id}")
def get_budget(route_id: str, db: DB, current_user: User = ManagerOrAdmin):
    return budget_service.get_budget(db, route_id, current_user)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_budget(body: BudgetCreate, db: DB, current_user: User = ManagerOrAdmin):
    data = body.model_dump(by_alias=False)
    return budget_service.create_budget(db, data, current_user)


@router.put("/{route_id}")
def update_budget(
    route_id: str,
    body: BudgetUpdate,
    db: DB,
    current_user: User = ManagerOrAdmin,
):
    data = body.model_dump(by_alias=False, exclude_none=True)
    return budget_service.update_budget(db, route_id, data, current_user)
