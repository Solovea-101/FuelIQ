import os
import logging

import numpy as np
import joblib

logger = logging.getLogger(__name__)

_model = None
_model_metadata = None


def load_model(model_path: str) -> bool:
    global _model, _model_metadata
    if not os.path.exists(model_path):
        logger.warning(f"ML model not found at {model_path}. Predictions will use fallback formula.")
        return False

    try:
        _model = joblib.load(model_path)
        metadata_path = model_path.replace(".joblib", "_metadata.json")
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path) as f:
                _model_metadata = json.load(f)
        logger.info("ML model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        return False


def predict_fuel(
    distance_km: float,
    avg_speed_kmh: float,
    max_speed_kmh: float | None = None,
    idle_time_minutes: float | None = None,
    engine_size_l: float | None = None,
    cylinders: int | None = None,
    fuel_type: str | None = None,
    route_type: str | None = None,
    load_weight_kg: float | None = None,
) -> dict:
    # Default values
    engine_size = engine_size_l or 2.5
    cyls = cylinders or 4
    max_spd = max_speed_kmh or avg_speed_kmh * 1.3
    idle = idle_time_minutes or 0.0
    ft = fuel_type or "diesel"
    rt = route_type or "mixed"
    load = load_weight_kg or 500.0

    if _model is not None:
        try:
            import pandas as pd

            duration = (distance_km / avg_speed_kmh) * 60 if avg_speed_kmh > 0 else 60
            speed_var = max_spd / max(avg_speed_kmh, 1)
            idle_rat = idle / max(duration, 1)
            dist_per_hr = distance_km / max(duration / 60, 0.01)

            features = pd.DataFrame([{
                "engine_size_l": engine_size,
                "cylinders": cyls,
                "distance_km": distance_km,
                "duration_minutes": duration,
                "avg_speed_kmh": avg_speed_kmh,
                "max_speed_kmh": max_spd,
                "idle_time_minutes": idle,
                "load_weight_kg": load,
                "speed_variance": speed_var,
                "idle_ratio": idle_rat,
                "distance_per_hour": dist_per_hr,
                "fuel_type": ft,
                "route_type": rt,
            }])

            predicted_fuel = float(_model.predict(features)[0])
        except Exception as e:
            logger.error(f"ML prediction failed, using fallback: {e}")
            predicted_fuel = _fallback_prediction(
                distance_km, avg_speed_kmh, engine_size, idle, ft
            )
    else:
        predicted_fuel = _fallback_prediction(
            distance_km, avg_speed_kmh, engine_size, idle, ft
        )

    predicted_fuel = max(predicted_fuel, 0.1)
    efficiency_kmpl = distance_km / predicted_fuel if predicted_fuel > 0 else 0

    # Compute efficiency score (0-100)
    baseline_kmpl = 12.0 if ft == "diesel" else 10.0
    efficiency_score = min(100, max(0, (efficiency_kmpl / baseline_kmpl) * 70))

    recommendations = _generate_recommendations(
        avg_speed_kmh, max_spd, idle, efficiency_kmpl, baseline_kmpl
    )

    return {
        "predictedFuelLiters": round(predicted_fuel, 2),
        "predictedEfficiencyKmpl": round(efficiency_kmpl, 2),
        "efficiencyScore": round(efficiency_score, 1),
        "recommendations": recommendations,
    }


def _fallback_prediction(
    distance_km: float,
    avg_speed_kmh: float,
    engine_size_l: float,
    idle_time_minutes: float,
    fuel_type: str,
) -> float:
    """Simple formula-based prediction as fallback."""
    # Base consumption: roughly 10-15 L/100km depending on engine
    base_l_per_100km = 8.0 + (engine_size_l - 1.5) * 2.5

    if fuel_type == "diesel":
        base_l_per_100km *= 0.85  # Diesel more efficient

    # Speed factor: optimal around 60-80 km/h
    if avg_speed_kmh < 30:
        speed_factor = 1.3  # City driving penalty
    elif avg_speed_kmh > 100:
        speed_factor = 1.2  # Highway high-speed penalty
    else:
        speed_factor = 1.0

    # Idle factor
    duration_hours = distance_km / max(avg_speed_kmh, 1)
    idle_ratio = idle_time_minutes / max(duration_hours * 60, 1)
    idle_factor = 1.0 + idle_ratio * 0.15

    fuel = (base_l_per_100km / 100) * distance_km * speed_factor * idle_factor
    noise = np.random.normal(0, fuel * 0.03)
    return fuel + noise


def _generate_recommendations(
    avg_speed: float,
    max_speed: float,
    idle_time: float,
    efficiency: float,
    baseline: float,
) -> list[str]:
    recs = []
    if idle_time > 10:
        recs.append("Reduce idle time to improve fuel efficiency")
    if max_speed > 110:
        recs.append("Reduce maximum speed to save fuel")
    if avg_speed < 25:
        recs.append("Consider alternative routes to avoid heavy traffic")
    if efficiency < baseline * 0.7:
        recs.append("Efficiency is below baseline — consider vehicle maintenance check")
    if max_speed > avg_speed * 2:
        recs.append("Maintain steadier speed to optimize fuel consumption")
    if not recs:
        recs.append("Good driving! Keep maintaining current driving patterns")
    return recs
