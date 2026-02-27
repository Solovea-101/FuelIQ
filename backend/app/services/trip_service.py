import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.trip import Trip, TripStatus, GPSWaypoint
from app.models.vehicle import Vehicle
from app.models.user import User
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import settings


def _trip_to_response(db: Session, trip: Trip) -> dict:
    driver = db.query(User).filter(User.id == trip.driver_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()

    waypoints = (
        db.query(GPSWaypoint)
        .filter(GPSWaypoint.trip_id == trip.id)
        .order_by(GPSWaypoint.sequence_order)
        .all()
    )

    start_location = {
        "latitude": trip.start_latitude,
        "longitude": trip.start_longitude,
        "altitude": trip.start_altitude,
        "accuracy": trip.start_accuracy,
        "speed": trip.start_speed,
        "heading": trip.start_heading,
        "timestamp": trip.start_location_timestamp or trip.start_time.isoformat(),
    }

    end_location = None
    if trip.end_latitude is not None:
        end_location = {
            "latitude": trip.end_latitude,
            "longitude": trip.end_longitude,
            "altitude": trip.end_altitude,
            "accuracy": trip.end_accuracy,
            "speed": trip.end_speed,
            "heading": trip.end_heading,
            "timestamp": trip.end_location_timestamp or (trip.end_time.isoformat() if trip.end_time else ""),
        }

    return {
        "id": trip.id,
        "driverId": trip.driver_id,
        "driverName": driver.name if driver else "Unknown",
        "vehicleId": trip.vehicle_id,
        "vehicleRegistration": vehicle.registration_number if vehicle else "Unknown",
        "startLocation": start_location,
        "endLocation": end_location,
        "waypoints": [
            {
                "latitude": w.latitude,
                "longitude": w.longitude,
                "altitude": w.altitude,
                "accuracy": w.accuracy,
                "speed": w.speed,
                "heading": w.heading,
                "timestamp": w.timestamp,
            }
            for w in waypoints
        ],
        "startTime": trip.start_time.isoformat() if trip.start_time else "",
        "endTime": trip.end_time.isoformat() if trip.end_time else None,
        "status": trip.status.value,
        "distanceKm": trip.distance_km or 0,
        "fuelUsedLiters": trip.fuel_used_liters,
        "fuelEfficiency": trip.fuel_efficiency,
        "fuelCostKES": trip.fuel_cost_kes,
        "route": trip.route,
        "notes": trip.notes,
    }


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def list_trips(
    db: Session,
    user: User,
    status: str | None = None,
    driver_id: str | None = None,
    vehicle_id: str | None = None,
) -> list[dict]:
    query = db.query(Trip).filter(Trip.company_id == user.company_id)

    if user.role.value == "driver":
        query = query.filter(Trip.driver_id == user.id)

    if status:
        query = query.filter(Trip.status == TripStatus(status))
    if driver_id:
        query = query.filter(Trip.driver_id == driver_id)
    if vehicle_id:
        query = query.filter(Trip.vehicle_id == vehicle_id)

    trips = query.order_by(Trip.start_time.desc()).all()
    return [_trip_to_response(db, t) for t in trips]


def get_trip(db: Session, trip_id: str, user: User) -> dict:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise NotFoundException("Trip not found")
    if trip.company_id != user.company_id and user.role.value != "admin":
        raise NotFoundException("Trip not found")
    return _trip_to_response(db, trip)


def get_active_trip(db: Session, user: User) -> dict | None:
    trip = (
        db.query(Trip)
        .filter(Trip.driver_id == user.id, Trip.status == TripStatus.in_progress)
        .first()
    )
    if not trip:
        return None
    return _trip_to_response(db, trip)


def create_trip(db: Session, data: dict, user: User) -> dict:
    start_loc = data["start_location"]
    vehicle = db.query(Vehicle).filter(Vehicle.id == data["vehicle_id"]).first()
    if not vehicle:
        raise BadRequestException("Vehicle not found")

    trip = Trip(
        driver_id=data["driver_id"],
        vehicle_id=data["vehicle_id"],
        company_id=user.company_id,
        start_latitude=start_loc["latitude"],
        start_longitude=start_loc["longitude"],
        start_altitude=start_loc.get("altitude"),
        start_accuracy=start_loc.get("accuracy"),
        start_speed=start_loc.get("speed"),
        start_heading=start_loc.get("heading"),
        start_location_timestamp=start_loc.get("timestamp"),
        status=TripStatus.in_progress,
        route=data.get("route"),
        notes=data.get("notes"),
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return _trip_to_response(db, trip)


def end_trip(db: Session, trip_id: str, data: dict, user: User) -> dict:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise NotFoundException("Trip not found")
    if trip.status != TripStatus.in_progress:
        raise BadRequestException("Trip is not in progress")

    end_loc = data["end_location"]
    trip.end_latitude = end_loc["latitude"]
    trip.end_longitude = end_loc["longitude"]
    trip.end_altitude = end_loc.get("altitude")
    trip.end_accuracy = end_loc.get("accuracy")
    trip.end_speed = end_loc.get("speed")
    trip.end_heading = end_loc.get("heading")
    trip.end_location_timestamp = end_loc.get("timestamp")
    trip.end_time = datetime.now(timezone.utc)
    trip.status = TripStatus.completed

    if data.get("notes"):
        trip.notes = data["notes"]

    # Compute distance from waypoints
    waypoints = (
        db.query(GPSWaypoint)
        .filter(GPSWaypoint.trip_id == trip.id)
        .order_by(GPSWaypoint.sequence_order)
        .all()
    )

    if waypoints:
        total_distance = 0.0
        speeds = []
        max_speed = 0.0
        idle_time = 0.0

        prev_lat, prev_lon = trip.start_latitude, trip.start_longitude
        for wp in waypoints:
            d = _haversine(prev_lat, prev_lon, wp.latitude, wp.longitude)
            total_distance += d
            prev_lat, prev_lon = wp.latitude, wp.longitude
            if wp.speed is not None:
                speeds.append(wp.speed)
                max_speed = max(max_speed, wp.speed)
                if wp.speed < 2.0:  # ~7 km/h threshold for idle
                    idle_time += 0.5  # assume ~30 second intervals

        # Add last segment to end location
        total_distance += _haversine(prev_lat, prev_lon, end_loc["latitude"], end_loc["longitude"])
        trip.distance_km = round(total_distance, 2)
        trip.avg_speed_kmh = round(sum(speeds) / len(speeds) * 3.6, 2) if speeds else None  # m/s to km/h
        trip.max_speed_kmh = round(max_speed * 3.6, 2) if max_speed > 0 else None
        trip.idle_time_minutes = round(idle_time, 1)
    else:
        # Just use start/end distance
        trip.distance_km = round(
            _haversine(
                trip.start_latitude, trip.start_longitude,
                end_loc["latitude"], end_loc["longitude"],
            ),
            2,
        )

    # Fuel metrics
    fuel_used = data.get("fuel_used_liters")
    if fuel_used:
        trip.fuel_used_liters = fuel_used
        trip.fuel_cost_kes = round(fuel_used * settings.FUEL_PRICE_KES, 2)
        if trip.distance_km > 0:
            trip.fuel_efficiency = round(trip.distance_km / fuel_used, 2)

    db.commit()
    db.refresh(trip)
    return _trip_to_response(db, trip)


def cancel_trip(db: Session, trip_id: str, user: User) -> None:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise NotFoundException("Trip not found")
    if trip.status not in (TripStatus.pending, TripStatus.in_progress):
        raise BadRequestException("Trip cannot be cancelled")
    trip.status = TripStatus.cancelled
    db.commit()


def add_waypoints(db: Session, trip_id: str, waypoints_data: list[dict]) -> None:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise NotFoundException("Trip not found")
    if trip.status != TripStatus.in_progress:
        raise BadRequestException("Trip is not in progress")

    # Get current max sequence order
    max_seq = (
        db.query(func.max(GPSWaypoint.sequence_order))
        .filter(GPSWaypoint.trip_id == trip_id)
        .scalar()
    ) or 0

    for i, wp in enumerate(waypoints_data):
        db_wp = GPSWaypoint(
            trip_id=trip_id,
            latitude=wp["latitude"],
            longitude=wp["longitude"],
            altitude=wp.get("altitude"),
            accuracy=wp.get("accuracy"),
            speed=wp.get("speed"),
            heading=wp.get("heading"),
            timestamp=wp["timestamp"],
            sequence_order=max_seq + i + 1,
        )
        db.add(db_wp)

    db.commit()
