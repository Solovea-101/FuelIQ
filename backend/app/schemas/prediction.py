from pydantic import Field

from app.schemas.common import CamelModel


class PredictionRequest(CamelModel):
    vehicle_id: str | None = Field(None, alias="vehicleId")
    distance_km: float = Field(alias="distanceKm")
    avg_speed_kmh: float = Field(alias="avgSpeedKmh")
    max_speed_kmh: float | None = Field(None, alias="maxSpeedKmh")
    idle_time_minutes: float | None = Field(None, alias="idleTimeMinutes")
    route_type: str | None = Field(None, alias="routeType")
    load_weight_kg: float | None = Field(None, alias="loadWeightKg")

    # Vehicle features (used if vehicleId not provided)
    engine_size_l: float | None = Field(None, alias="engineSizeL")
    cylinders: int | None = None
    fuel_type: str | None = Field(None, alias="fuelType")


class PredictionResponse(CamelModel):
    predicted_fuel_liters: float = Field(alias="predictedFuelLiters")
    predicted_efficiency_kmpl: float = Field(alias="predictedEfficiencyKmpl")
    efficiency_score: float = Field(alias="efficiencyScore")
    recommendations: list[str]
