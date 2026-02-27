from fastapi import APIRouter, Depends

from app.core.dependencies import DB, require_role
from app.models.user import User, UserRole
from app.models.trip import Trip, TripStatus
from app.models.vehicle import Vehicle
from app.core.exceptions import NotFoundException
from sqlalchemy import func

router = APIRouter(prefix="/admin", tags=["admin"])

AdminOnly = Depends(require_role("admin"))


@router.get("/users")
def list_users(db: DB, current_user: User = AdminOnly):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "phone": u.phone,
            "role": u.role.value,
            "companyId": u.company_id,
            "companyName": u.company.name,
            "createdAt": u.created_at.isoformat() if u.created_at else "",
        }
        for u in users
    ]


@router.patch("/users/{user_id}")
def update_user(user_id: str, body: dict, db: DB, current_user: User = AdminOnly):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")

    if "role" in body:
        user.role = UserRole(body["role"])
    if "name" in body:
        user.name = body["name"]

    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "companyId": user.company_id,
    }


@router.get("/analytics")
def system_analytics(db: DB, current_user: User = AdminOnly):
    total_users = db.query(func.count(User.id)).scalar()
    total_trips = db.query(func.count(Trip.id)).filter(Trip.status == TripStatus.completed).scalar()
    total_fuel = db.query(func.coalesce(func.sum(Trip.fuel_used_liters), 0)).filter(Trip.status == TripStatus.completed).scalar()
    total_vehicles = db.query(func.count(Vehicle.id)).scalar()

    return {
        "totalUsers": total_users,
        "totalTrips": total_trips,
        "totalFuelUsedLiters": round(float(total_fuel), 2),
        "totalVehicles": total_vehicles,
    }


@router.get("/settings")
def system_settings(current_user: User = AdminOnly):
    return {
        "fuelPriceKES": 180.0,
        "defaultCurrency": "KES",
        "mlModelLoaded": True,
    }
