from pydantic import Field

from app.schemas.common import CamelModel


class VehicleCreate(CamelModel):
    registration_number: str = Field(alias="registrationNumber")
    make: str
    model: str
    year: int
    fuel_type: str = Field(alias="fuelType")
    tank_capacity_liters: float = Field(alias="tankCapacityLiters")
    odometer_km: float = Field(0.0, alias="odometerKm")
    engine_size_l: float | None = Field(None, alias="engineSizeL")
    cylinders: int | None = None


class VehicleUpdate(CamelModel):
    status: str | None = None
    odometer_km: float | None = Field(None, alias="odometerKm")
    assigned_driver_id: str | None = Field(None, alias="assignedDriverId")
    last_service_date: str | None = Field(None, alias="lastServiceDate")
    next_service_km: float | None = Field(None, alias="nextServiceKm")


class VehicleAssign(CamelModel):
    driver_id: str = Field(alias="driverId")
    driver_name: str = Field(alias="driverName")


class VehicleResponse(CamelModel):
    id: str
    registration_number: str = Field(alias="registrationNumber")
    make: str
    model: str
    year: int
    fuel_type: str = Field(alias="fuelType")
    tank_capacity_liters: float = Field(alias="tankCapacityLiters")
    odometer_km: float = Field(alias="odometerKm")
    status: str
    assigned_driver_id: str | None = Field(None, alias="assignedDriverId")
    assigned_driver_name: str | None = Field(None, alias="assignedDriverName")
    last_service_date: str | None = Field(None, alias="lastServiceDate")
    next_service_km: float | None = Field(None, alias="nextServiceKm")
    average_efficiency: float | None = Field(None, alias="averageEfficiency")
    total_trips: int | None = Field(None, alias="totalTrips")
    total_distance_km: float | None = Field(None, alias="totalDistanceKm")
