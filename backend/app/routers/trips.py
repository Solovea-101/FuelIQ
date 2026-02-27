from fastapi import APIRouter, status

from app.core.dependencies import DB, CurrentUser
from app.schemas.trip import TripCreate, TripEnd, WaypointBatch
from app.services import trip_service

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("")
def list_trips(
    db: DB,
    current_user: CurrentUser,
    status_filter: str | None = None,
    driver_id: str | None = None,
    vehicle_id: str | None = None,
):
    return trip_service.list_trips(db, current_user, status=status_filter, driver_id=driver_id, vehicle_id=vehicle_id)


@router.get("/active")
def get_active_trip(db: DB, current_user: CurrentUser):
    trip = trip_service.get_active_trip(db, current_user)
    return trip


@router.get("/{trip_id}")
def get_trip(trip_id: str, db: DB, current_user: CurrentUser):
    return trip_service.get_trip(db, trip_id, current_user)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_trip(body: TripCreate, db: DB, current_user: CurrentUser):
    data = {
        "vehicle_id": body.vehicle_id,
        "driver_id": body.driver_id,
        "start_location": body.start_location.model_dump(),
        "route": body.route,
        "notes": body.notes,
    }
    return trip_service.create_trip(db, data, current_user)


@router.post("/{trip_id}/end")
def end_trip(trip_id: str, body: TripEnd, db: DB, current_user: CurrentUser):
    data = {
        "end_location": body.end_location.model_dump(),
        "fuel_used_liters": body.fuel_used_liters,
        "notes": body.notes,
    }
    return trip_service.end_trip(db, trip_id, data, current_user)


@router.post("/{trip_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_trip(trip_id: str, db: DB, current_user: CurrentUser):
    trip_service.cancel_trip(db, trip_id, current_user)
    return {"message": "Trip cancelled"}


@router.post("/{trip_id}/waypoints", status_code=status.HTTP_201_CREATED)
def add_waypoints(trip_id: str, body: WaypointBatch, db: DB, current_user: CurrentUser):
    waypoints_data = [w.model_dump() for w in body.waypoints]
    trip_service.add_waypoints(db, trip_id, waypoints_data)
    return {"message": f"Added {len(waypoints_data)} waypoints"}
