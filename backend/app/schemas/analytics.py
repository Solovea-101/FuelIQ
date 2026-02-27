from pydantic import Field

from app.schemas.common import CamelModel


class FuelEfficiencyMetrics(CamelModel):
    average_km_per_liter: float = Field(alias="averageKmPerLiter")
    total_fuel_used_liters: float = Field(alias="totalFuelUsedLiters")
    total_distance_km: float = Field(alias="totalDistanceKm")
    total_cost_kes: float = Field(alias="totalCostKES")
    trend: str
    comparison_period: str = Field(alias="comparisonPeriod")
    change_percent: float = Field(alias="changePercent")


class DailyFuelData(CamelModel):
    date: str
    fuel_liters: float = Field(alias="fuelLiters")
    distance_km: float = Field(alias="distanceKm")
    efficiency: float
    cost_kes: float = Field(alias="costKES")


class RecommendationResponse(CamelModel):
    id: str
    type: str
    title: str
    description: str
    priority: str
    potential_savings_kes: float | None = Field(None, alias="potentialSavingsKES")
    affected_vehicles: list[str] | None = Field(None, alias="affectedVehicles")
    affected_drivers: list[str] | None = Field(None, alias="affectedDrivers")
    created_at: str = Field(alias="createdAt")


class AnalyticsSummaryResponse(CamelModel):
    fuel_efficiency: FuelEfficiencyMetrics = Field(alias="fuelEfficiency")
    recommendations: list[RecommendationResponse]
    daily_data: list[DailyFuelData] = Field(alias="dailyData")
