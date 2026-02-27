from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vehicle import Vehicle, VehicleStatus, FuelType
from app.models.user import User
from app.models.trip import Trip, TripStatus
from app.core.exceptions import NotFoundException, BadRequestException


def _vehicle_to_response(db: Session, vehicle: Vehicle) -> dict:
    # Compute aggregates from trips
    trip_stats = (
        db.query(
            func.count(Trip.id).label("total_trips"),
            func.coalesce(func.sum(Trip.distance_km), 0).label("total_distance"),
            func.avg(Trip.fuel_efficiency).label("avg_efficiency"),
        )
        .filter(Trip.vehicle_id == vehicle.id, Trip.status == TripStatus.completed)
        .first()
    )

    driver_name = None
    if vehicle.assigned_driver_id:
        driver = db.query(User).filter(User.id == vehicle.assigned_driver_id).first()
        if driver:
            driver_name = driver.name

    return {
        "id": vehicle.id,
        "registrationNumber": vehicle.registration_number,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "fuelType": vehicle.fuel_type.value,
        "tankCapacityLiters": vehicle.tank_capacity_liters,
        "odometerKm": vehicle.odometer_km,
        "status": vehicle.status.value,
        "assignedDriverId": vehicle.assigned_driver_id,
        "assignedDriverName": driver_name,
        "lastServiceDate": vehicle.last_service_date,
        "nextServiceKm": vehicle.next_service_km,
        "averageEfficiency": round(trip_stats.avg_efficiency, 2) if trip_stats.avg_efficiency else None,
        "totalTrips": trip_stats.total_trips or 0,
        "totalDistanceKm": round(float(trip_stats.total_distance or 0), 2),
    }


def list_vehicles(
    db: Session,
    user: User,
    status: str | None = None,
    fuel_type: str | None = None,
) -> list[dict]:
    query = db.query(Vehicle).filter(Vehicle.company_id == user.company_id)

    if user.role.value == "driver":
        query = query.filter(Vehicle.assigned_driver_id == user.id)

    if status:
        query = query.filter(Vehicle.status == VehicleStatus(status))
    if fuel_type:
        query = query.filter(Vehicle.fuel_type == FuelType(fuel_type))

    vehicles = query.all()
    return [_vehicle_to_response(db, v) for v in vehicles]


def get_vehicle(db: Session, vehicle_id: str, user: User) -> dict:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    if vehicle.company_id != user.company_id and user.role.value != "admin":
        raise NotFoundException("Vehicle not found")
    return _vehicle_to_response(db, vehicle)


def create_vehicle(db: Session, data: dict, user: User) -> dict:
    vehicle = Vehicle(
        registration_number=data["registration_number"],
        make=data["make"],
        model=data["model"],
        year=data["year"],
        fuel_type=FuelType(data["fuel_type"]),
        tank_capacity_liters=data["tank_capacity_liters"],
        odometer_km=data.get("odometer_km", 0.0),
        engine_size_l=data.get("engine_size_l"),
        cylinders=data.get("cylinders"),
        company_id=user.company_id,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return _vehicle_to_response(db, vehicle)


def update_vehicle(db: Session, vehicle_id: str, data: dict, user: User) -> dict:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    if vehicle.company_id != user.company_id and user.role.value != "admin":
        raise NotFoundException("Vehicle not found")

    for key, value in data.items():
        if value is not None and hasattr(vehicle, key):
            if key == "status":
                setattr(vehicle, key, VehicleStatus(value))
            else:
                setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)
    return _vehicle_to_response(db, vehicle)


def delete_vehicle(db: Session, vehicle_id: str, user: User) -> None:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    if vehicle.company_id != user.company_id and user.role.value != "admin":
        raise NotFoundException("Vehicle not found")
    db.delete(vehicle)
    db.commit()


def assign_driver(db: Session, vehicle_id: str, driver_id: str, user: User) -> dict:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    if vehicle.company_id != user.company_id and user.role.value != "admin":
        raise NotFoundException("Vehicle not found")

    driver = db.query(User).filter(User.id == driver_id).first()
    if not driver:
        raise BadRequestException("Driver not found")

    vehicle.assigned_driver_id = driver_id
    db.commit()
    db.refresh(vehicle)
    return _vehicle_to_response(db, vehicle)


def unassign_driver(db: Session, vehicle_id: str, user: User) -> dict:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise NotFoundException("Vehicle not found")
    if vehicle.company_id != user.company_id and user.role.value != "admin":
        raise NotFoundException("Vehicle not found")

    vehicle.assigned_driver_id = None
    db.commit()
    db.refresh(vehicle)
    return _vehicle_to_response(db, vehicle)
