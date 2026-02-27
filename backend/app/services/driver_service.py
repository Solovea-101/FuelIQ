from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.models.trip import Trip, TripStatus
from app.core.exceptions import NotFoundException


def list_drivers(db: Session, user: User) -> list[dict]:
    drivers = (
        db.query(User)
        .filter(User.company_id == user.company_id, User.role == UserRole.driver)
        .all()
    )
    return [_driver_to_response(db, d) for d in drivers]


def get_driver(db: Session, driver_id: str, user: User) -> dict:
    driver = db.query(User).filter(User.id == driver_id, User.role == UserRole.driver).first()
    if not driver:
        raise NotFoundException("Driver not found")
    if driver.company_id != user.company_id and user.role.value != "admin":
        raise NotFoundException("Driver not found")
    return _driver_to_response(db, driver)


def get_driver_performance(db: Session, user: User) -> list[dict]:
    drivers = (
        db.query(User)
        .filter(User.company_id == user.company_id, User.role == UserRole.driver)
        .all()
    )

    performances = []
    for driver in drivers:
        stats = (
            db.query(
                func.count(Trip.id).label("total_trips"),
                func.coalesce(func.sum(Trip.distance_km), 0).label("total_distance"),
                func.coalesce(func.sum(Trip.fuel_used_liters), 0).label("total_fuel"),
                func.avg(Trip.fuel_efficiency).label("avg_efficiency"),
            )
            .filter(Trip.driver_id == driver.id, Trip.status == TripStatus.completed)
            .first()
        )

        avg_eff = float(stats.avg_efficiency) if stats.avg_efficiency else 0.0
        performances.append({
            "driverId": driver.id,
            "driverName": driver.name,
            "totalTrips": stats.total_trips or 0,
            "totalDistanceKm": round(float(stats.total_distance or 0), 2),
            "totalFuelUsedLiters": round(float(stats.total_fuel or 0), 2),
            "averageEfficiency": round(avg_eff, 2),
            "efficiencyTrend": "stable",
            "ranking": 0,
        })

    # Sort by efficiency descending and assign rankings
    performances.sort(key=lambda x: x["averageEfficiency"], reverse=True)
    for i, p in enumerate(performances):
        p["ranking"] = i + 1

    return performances


def _driver_to_response(db: Session, driver: User) -> dict:
    stats = (
        db.query(
            func.count(Trip.id).label("total_trips"),
            func.coalesce(func.sum(Trip.distance_km), 0).label("total_distance"),
            func.avg(Trip.fuel_efficiency).label("avg_efficiency"),
        )
        .filter(Trip.driver_id == driver.id, Trip.status == TripStatus.completed)
        .first()
    )

    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.assigned_driver_id == driver.id)
        .first()
    )

    return {
        "id": driver.id,
        "name": driver.name,
        "email": driver.email,
        "phone": driver.phone,
        "status": "active",
        "assignedVehicleId": vehicle.id if vehicle else None,
        "assignedVehicleRegistration": vehicle.registration_number if vehicle else None,
        "totalTrips": stats.total_trips or 0,
        "totalDistanceKm": round(float(stats.total_distance or 0), 2),
        "averageEfficiency": round(float(stats.avg_efficiency), 2) if stats.avg_efficiency else None,
        "joinedAt": driver.created_at.isoformat() if driver.created_at else "",
    }
