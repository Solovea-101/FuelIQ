from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.user import User
from app.core.exceptions import NotFoundException


def list_budgets(db: Session, user: User) -> list[dict]:
    budgets = db.query(Budget).filter(Budget.company_id == user.company_id).all()
    return [_budget_to_response(b) for b in budgets]


def get_budget(db: Session, route_id: str, user: User) -> dict:
    budget = (
        db.query(Budget)
        .filter(Budget.route_id == route_id, Budget.company_id == user.company_id)
        .first()
    )
    if not budget:
        raise NotFoundException("Budget not found")
    return _budget_to_response(budget)


def create_budget(db: Session, data: dict, user: User) -> dict:
    budget = Budget(
        company_id=user.company_id,
        route_id=data["route_id"],
        route_name=data["route_name"],
        monthly_budget_kes=data["monthly_budget_kes"],
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _budget_to_response(budget)


def update_budget(db: Session, route_id: str, data: dict, user: User) -> dict:
    budget = (
        db.query(Budget)
        .filter(Budget.route_id == route_id, Budget.company_id == user.company_id)
        .first()
    )
    if not budget:
        raise NotFoundException("Budget not found")

    for key, value in data.items():
        if value is not None and hasattr(budget, key):
            setattr(budget, key, value)

    db.commit()
    db.refresh(budget)
    return _budget_to_response(budget)


def _budget_to_response(budget: Budget) -> dict:
    return {
        "id": budget.id,
        "routeId": budget.route_id,
        "routeName": budget.route_name,
        "monthlyBudgetKES": budget.monthly_budget_kes,
    }
