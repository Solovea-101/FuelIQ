import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from app.models.trip import Trip, TripStatus
from app.models.recommendation import Recommendation
from app.models.user import User
from app.config import settings


def get_fuel_efficiency(db: Session, user: User) -> dict:
    query = db.query(Trip).filter(
        Trip.company_id == user.company_id,
        Trip.status == TripStatus.completed,
    )

    stats = db.query(
        func.coalesce(func.sum(Trip.distance_km), 0).label("total_distance"),
        func.coalesce(func.sum(Trip.fuel_used_liters), 0).label("total_fuel"),
        func.avg(Trip.fuel_efficiency).label("avg_efficiency"),
    ).filter(
        Trip.company_id == user.company_id,
        Trip.status == TripStatus.completed,
    ).first()

    total_distance = float(stats.total_distance or 0)
    total_fuel = float(stats.total_fuel or 0)
    avg_eff = float(stats.avg_efficiency) if stats.avg_efficiency else 0.0
    total_cost = round(total_fuel * settings.FUEL_PRICE_KES, 2)

    return {
        "averageKmPerLiter": round(avg_eff, 2),
        "totalFuelUsedLiters": round(total_fuel, 2),
        "totalDistanceKm": round(total_distance, 2),
        "totalCostKES": total_cost,
        "trend": "stable",
        "comparisonPeriod": "vs last month",
        "changePercent": 0.0,
    }


def get_daily_data(db: Session, user: User, days: int = 14) -> list[dict]:
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    results = (
        db.query(
            func.date(Trip.start_time).label("date"),
            func.coalesce(func.sum(Trip.fuel_used_liters), 0).label("fuel"),
            func.coalesce(func.sum(Trip.distance_km), 0).label("distance"),
            func.avg(Trip.fuel_efficiency).label("efficiency"),
        )
        .filter(
            Trip.company_id == user.company_id,
            Trip.status == TripStatus.completed,
            Trip.start_time >= start_date,
        )
        .group_by(func.date(Trip.start_time))
        .order_by(func.date(Trip.start_time))
        .all()
    )

    return [
        {
            "date": str(r.date),
            "fuelLiters": round(float(r.fuel or 0), 2),
            "distanceKm": round(float(r.distance or 0), 2),
            "efficiency": round(float(r.efficiency), 2) if r.efficiency else 0.0,
            "costKES": round(float(r.fuel or 0) * settings.FUEL_PRICE_KES, 2),
        }
        for r in results
    ]


def get_recommendations(db: Session, user: User) -> list[dict]:
    recs = (
        db.query(Recommendation)
        .filter(
            Recommendation.company_id == user.company_id,
            Recommendation.is_active == True,
        )
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "type": r.type.value,
            "title": r.title,
            "description": r.description,
            "priority": r.priority.value,
            "potentialSavingsKES": r.potential_savings_kes,
            "affectedVehicles": json.loads(r.affected_vehicles) if r.affected_vehicles else None,
            "affectedDrivers": json.loads(r.affected_drivers) if r.affected_drivers else None,
            "createdAt": r.created_at.isoformat() if r.created_at else "",
        }
        for r in recs
    ]


def get_summary(db: Session, user: User) -> dict:
    return {
        "fuelEfficiency": get_fuel_efficiency(db, user),
        "recommendations": get_recommendations(db, user),
        "dailyData": get_daily_data(db, user),
    }
