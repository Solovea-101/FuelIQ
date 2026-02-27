from pydantic import Field

from app.schemas.common import CamelModel


class GPSCoordinateSchema(CamelModel):
    latitude: float
    longitude: float
    altitude: float | None = None
    accuracy: float | None = None
    speed: float | None = None
    heading: float | None = None
    timestamp: str


class TripCreate(CamelModel):
    vehicle_id: str = Field(alias="vehicleId")
    driver_id: str = Field(alias="driverId")
    start_location: GPSCoordinateSchema = Field(alias="startLocation")
    route: str | None = None
    notes: str | None = None


class TripEnd(CamelModel):
    trip_id: str = Field(alias="tripId")
    end_location: GPSCoordinateSchema = Field(alias="endLocation")
    fuel_used_liters: float | None = Field(None, alias="fuelUsedLiters")
    notes: str | None = None


class WaypointBatch(CamelModel):
    waypoints: list[GPSCoordinateSchema]


class TripResponse(CamelModel):
    id: str
    driver_id: str = Field(alias="driverId")
    driver_name: str = Field(alias="driverName")
    vehicle_id: str = Field(alias="vehicleId")
    vehicle_registration: str = Field(alias="vehicleRegistration")
    start_location: GPSCoordinateSchema = Field(alias="startLocation")
    end_location: GPSCoordinateSchema | None = Field(None, alias="endLocation")
    waypoints: list[GPSCoordinateSchema] = []
    start_time: str = Field(alias="startTime")
    end_time: str | None = Field(None, alias="endTime")
    status: str
    distance_km: float = Field(alias="distanceKm")
    fuel_used_liters: float | None = Field(None, alias="fuelUsedLiters")
    fuel_efficiency: float | None = Field(None, alias="fuelEfficiency")
    fuel_cost_kes: float | None = Field(None, alias="fuelCostKES")
    route: str | None = None
    notes: str | None = None
