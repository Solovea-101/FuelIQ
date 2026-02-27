from fastapi import APIRouter

from app.core.dependencies import DB, CurrentUser
from app.models.vehicle import Vehicle
from app.schemas.prediction import PredictionRequest
from app.services import prediction_service

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("/fuel-consumption")
def predict_fuel_consumption(body: PredictionRequest, db: DB, current_user: CurrentUser):
    engine_size = body.engine_size_l
    cylinders = body.cylinders
    fuel_type = body.fuel_type

    if body.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == body.vehicle_id).first()
        if vehicle:
            engine_size = engine_size or vehicle.engine_size_l
            cylinders = cylinders or vehicle.cylinders
            fuel_type = fuel_type or vehicle.fuel_type.value

    return prediction_service.predict_fuel(
        distance_km=body.distance_km,
        avg_speed_kmh=body.avg_speed_kmh,
        max_speed_kmh=body.max_speed_kmh,
        idle_time_minutes=body.idle_time_minutes,
        engine_size_l=engine_size,
        cylinders=cylinders,
        fuel_type=fuel_type,
        route_type=body.route_type,
        load_weight_kg=body.load_weight_kg,
    )
