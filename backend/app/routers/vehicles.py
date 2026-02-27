from fastapi import APIRouter, Depends, status

from app.core.dependencies import DB, CurrentUser, require_role
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleAssign
from app.services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

ManagerOrAdmin = Depends(require_role("fleet_manager", "admin"))


@router.get("")
def list_vehicles(
    db: DB,
    current_user: CurrentUser,
    status: str | None = None,
    fuel_type: str | None = None,
):
    return vehicle_service.list_vehicles(db, current_user, status=status, fuel_type=fuel_type)


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: DB, current_user: CurrentUser):
    return vehicle_service.get_vehicle(db, vehicle_id, current_user)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_vehicle(
    body: VehicleCreate,
    db: DB,
    current_user: User = ManagerOrAdmin,
):
    data = body.model_dump(by_alias=False)
    return vehicle_service.create_vehicle(db, data, current_user)


@router.patch("/{vehicle_id}")
def update_vehicle(
    vehicle_id: str,
    body: VehicleUpdate,
    db: DB,
    current_user: User = ManagerOrAdmin,
):
    data = body.model_dump(by_alias=False, exclude_none=True)
    return vehicle_service.update_vehicle(db, vehicle_id, data, current_user)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str,
    db: DB,
    current_user: User = ManagerOrAdmin,
):
    vehicle_service.delete_vehicle(db, vehicle_id, current_user)


@router.post("/{vehicle_id}/assign")
def assign_driver(
    vehicle_id: str,
    body: VehicleAssign,
    db: DB,
    current_user: User = ManagerOrAdmin,
):
    return vehicle_service.assign_driver(db, vehicle_id, body.driver_id, current_user)


@router.post("/{vehicle_id}/unassign")
def unassign_driver(
    vehicle_id: str,
    db: DB,
    current_user: User = ManagerOrAdmin,
):
    return vehicle_service.unassign_driver(db, vehicle_id, current_user)
