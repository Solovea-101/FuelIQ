from pydantic import Field

from app.schemas.common import CamelModel


class DriverResponse(CamelModel):
    id: str
    name: str
    email: str
    phone: str | None = None
    status: str
    assigned_vehicle_id: str | None = Field(None, alias="assignedVehicleId")
    assigned_vehicle_registration: str | None = Field(None, alias="assignedVehicleRegistration")
    total_trips: int = Field(0, alias="totalTrips")
    total_distance_km: float = Field(0.0, alias="totalDistanceKm")
    average_efficiency: float | None = Field(None, alias="averageEfficiency")
    joined_at: str = Field(alias="joinedAt")


class DriverPerformanceResponse(CamelModel):
    driver_id: str = Field(alias="driverId")
    driver_name: str = Field(alias="driverName")
    total_trips: int = Field(alias="totalTrips")
    total_distance_km: float = Field(alias="totalDistanceKm")
    total_fuel_used_liters: float = Field(alias="totalFuelUsedLiters")
    average_efficiency: float = Field(alias="averageEfficiency")
    efficiency_trend: str = Field(alias="efficiencyTrend")
    ranking: int
