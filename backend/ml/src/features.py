"""Feature engineering for fuel consumption prediction."""
import pandas as pd
import numpy as np


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features to the dataset."""
    df = df.copy()

    # Speed variance indicator (max/avg ratio)
    df["speed_variance"] = df["max_speed_kmh"] / df["avg_speed_kmh"].clip(lower=1)

    # Idle ratio (fraction of trip spent idling)
    df["idle_ratio"] = df["idle_time_minutes"] / df["duration_minutes"].clip(lower=1)

    # Distance per hour
    df["distance_per_hour"] = df["distance_km"] / (df["duration_minutes"] / 60).clip(lower=0.01)

    # Engine displacement category
    df["engine_category"] = pd.cut(
        df["engine_size_l"],
        bins=[0, 2.0, 3.0, 4.0, 10.0],
        labels=["small", "medium", "large", "xlarge"],
    )

    return df


NUMERICAL_FEATURES = [
    "engine_size_l",
    "cylinders",
    "distance_km",
    "duration_minutes",
    "avg_speed_kmh",
    "max_speed_kmh",
    "idle_time_minutes",
    "load_weight_kg",
    "speed_variance",
    "idle_ratio",
    "distance_per_hour",
]

CATEGORICAL_FEATURES = [
    "fuel_type",
    "route_type",
]

TARGET = "fuel_used_liters"
