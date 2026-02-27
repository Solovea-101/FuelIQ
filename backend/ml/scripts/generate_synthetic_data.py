"""Generate synthetic trip data for ML model training."""
import numpy as np
import pandas as pd

np.random.seed(42)

NUM_RECORDS = 10000

# Vehicle configurations common in Kenyan fleets
VEHICLE_CONFIGS = [
    {"engine_size_l": 2.4, "cylinders": 4, "fuel_type": "diesel", "vehicle_class": "Pickup", "base_l_100km": 9.5},
    {"engine_size_l": 2.5, "cylinders": 4, "fuel_type": "diesel", "vehicle_class": "Pickup", "base_l_100km": 10.0},
    {"engine_size_l": 3.0, "cylinders": 4, "fuel_type": "diesel", "vehicle_class": "Pickup", "base_l_100km": 11.0},
    {"engine_size_l": 2.8, "cylinders": 4, "fuel_type": "diesel", "vehicle_class": "SUV", "base_l_100km": 10.5},
    {"engine_size_l": 4.5, "cylinders": 6, "fuel_type": "diesel", "vehicle_class": "SUV", "base_l_100km": 14.0},
    {"engine_size_l": 2.0, "cylinders": 4, "fuel_type": "petrol", "vehicle_class": "Sedan", "base_l_100km": 8.5},
    {"engine_size_l": 1.5, "cylinders": 4, "fuel_type": "petrol", "vehicle_class": "Compact", "base_l_100km": 7.0},
    {"engine_size_l": 3.5, "cylinders": 6, "fuel_type": "petrol", "vehicle_class": "SUV", "base_l_100km": 12.5},
    {"engine_size_l": 2.2, "cylinders": 4, "fuel_type": "diesel", "vehicle_class": "Van", "base_l_100km": 9.0},
    {"engine_size_l": 5.7, "cylinders": 8, "fuel_type": "diesel", "vehicle_class": "Truck", "base_l_100km": 18.0},
]

ROUTE_TYPES = ["urban", "highway", "mixed"]
TRAFFIC_LEVELS = ["low", "medium", "high"]
WEATHER_CONDITIONS = ["clear", "rain", "hot"]


def generate_data():
    records = []

    for _ in range(NUM_RECORDS):
        # Pick a random vehicle config
        config = VEHICLE_CONFIGS[np.random.randint(len(VEHICLE_CONFIGS))]

        # Trip features
        route_type = np.random.choice(ROUTE_TYPES, p=[0.35, 0.30, 0.35])
        traffic = np.random.choice(TRAFFIC_LEVELS, p=[0.3, 0.45, 0.25])
        weather = np.random.choice(WEATHER_CONDITIONS, p=[0.6, 0.25, 0.15])

        # Distance: varies by route type
        if route_type == "urban":
            distance_km = np.random.uniform(5, 50)
        elif route_type == "highway":
            distance_km = np.random.uniform(50, 500)
        else:
            distance_km = np.random.uniform(20, 200)

        # Speed: varies by route type and traffic
        base_speed = {"urban": 25, "highway": 80, "mixed": 50}[route_type]
        traffic_speed_factor = {"low": 1.15, "medium": 1.0, "high": 0.7}[traffic]
        avg_speed_kmh = base_speed * traffic_speed_factor + np.random.normal(0, 5)
        avg_speed_kmh = max(10, avg_speed_kmh)

        max_speed_kmh = avg_speed_kmh * np.random.uniform(1.2, 1.8)
        max_speed_kmh = min(max_speed_kmh, 140)

        # Duration from distance and speed
        duration_minutes = (distance_km / avg_speed_kmh) * 60

        # Idle time: more in urban, less on highway
        idle_base = {"urban": 0.2, "highway": 0.05, "mixed": 0.12}[route_type]
        traffic_idle_factor = {"low": 0.7, "medium": 1.0, "high": 1.5}[traffic]
        idle_time_minutes = duration_minutes * idle_base * traffic_idle_factor + np.random.exponential(2)
        idle_time_minutes = max(0, idle_time_minutes)

        # Load weight
        load_weight_kg = np.random.uniform(0, 2000) if config["vehicle_class"] in ["Pickup", "Truck", "Van"] else np.random.uniform(0, 500)

        # === COMPUTE FUEL CONSUMPTION ===
        baseline = config["base_l_100km"]

        # Speed factor: U-shaped, optimal at 60-80
        if avg_speed_kmh < 30:
            speed_factor = 1.25 + (30 - avg_speed_kmh) * 0.01
        elif avg_speed_kmh > 90:
            speed_factor = 1.0 + (avg_speed_kmh - 90) * 0.005
        elif 60 <= avg_speed_kmh <= 80:
            speed_factor = 0.95
        else:
            speed_factor = 1.0

        # Idle factor
        idle_ratio = idle_time_minutes / max(duration_minutes, 1)
        idle_factor = 1.0 + idle_ratio * 0.4

        # Load factor
        load_factor = 1.0 + (load_weight_kg / 5000) * 0.15

        # Traffic factor
        traffic_factor = {"low": 0.95, "medium": 1.0, "high": 1.15}[traffic]

        # Weather factor
        weather_factor = {"clear": 1.0, "rain": 1.05, "hot": 1.03}[weather]

        # Calculate fuel
        fuel_used_liters = (baseline / 100) * distance_km * speed_factor * idle_factor * load_factor * traffic_factor * weather_factor
        # Add noise
        fuel_used_liters += np.random.normal(0, fuel_used_liters * 0.05)
        fuel_used_liters = max(0.1, fuel_used_liters)

        records.append({
            "engine_size_l": config["engine_size_l"],
            "cylinders": config["cylinders"],
            "fuel_type": config["fuel_type"],
            "vehicle_class": config["vehicle_class"],
            "distance_km": round(distance_km, 2),
            "duration_minutes": round(duration_minutes, 2),
            "avg_speed_kmh": round(avg_speed_kmh, 2),
            "max_speed_kmh": round(max_speed_kmh, 2),
            "idle_time_minutes": round(idle_time_minutes, 2),
            "route_type": route_type,
            "load_weight_kg": round(load_weight_kg, 2),
            "traffic_level": traffic,
            "weather": weather,
            "fuel_used_liters": round(fuel_used_liters, 3),
        })

    df = pd.DataFrame(records)

    # Validate
    print(f"Generated {len(df)} synthetic trip records")
    print(f"\nFeature summary:")
    print(df.describe().round(2))
    print(f"\nFuel type distribution:\n{df['fuel_type'].value_counts()}")
    print(f"\nRoute type distribution:\n{df['route_type'].value_counts()}")
    print(f"\nTraffic distribution:\n{df['traffic_level'].value_counts()}")
    print(f"\nVehicle class distribution:\n{df['vehicle_class'].value_counts()}")

    # Save
    output_path = "ml/data/synthetic_trips.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")

    return df


if __name__ == "__main__":
    generate_data()
