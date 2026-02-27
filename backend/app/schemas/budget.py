from pydantic import Field

from app.schemas.common import CamelModel


class BudgetCreate(CamelModel):
    route_id: str = Field(alias="routeId")
    route_name: str = Field(alias="routeName")
    monthly_budget_kes: float = Field(alias="monthlyBudgetKES")


class BudgetUpdate(CamelModel):
    route_name: str | None = Field(None, alias="routeName")
    monthly_budget_kes: float | None = Field(None, alias="monthlyBudgetKES")


class BudgetResponse(CamelModel):
    id: str
    route_id: str = Field(alias="routeId")
    route_name: str = Field(alias="routeName")
    monthly_budget_kes: float = Field(alias="monthlyBudgetKES")
