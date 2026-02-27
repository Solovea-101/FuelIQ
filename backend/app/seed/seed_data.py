"""Seed development data for FuelIQ."""
import json
import uuid
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle, VehicleStatus, FuelType
from app.models.trip import Trip, TripStatus, GPSWaypoint
from app.models.recommendation import Recommendation, RecommendationType, Priority
from app.models.budget import Budget
from app.core.security import hash_password


def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Company).first():
            print("Database already seeded. Skipping.")
            return

        # Company
        company = Company(id="company-001", name="Safari Logistics Ltd")
        db.add(company)
        db.flush()

        # Users
        manager = User(
            id="manager-001",
            email="manager@fueliq.ke",
            password_hash=hash_password("manager123"),
            name="Alice Wambui",
            phone="+254700000001",
            role=UserRole.fleet_manager,
            company_id=company.id,
        )
        driver1 = User(
            id="driver-001",
            email="driver@fueliq.ke",
            password_hash=hash_password("driver123"),
            name="John Kamau",
            phone="+254700000002",
            role=UserRole.driver,
            company_id=company.id,
        )
        driver2 = User(
            id="driver-002",
            email="peter.ochieng@fueliq.ke",
            password_hash=hash_password("password123"),
            name="Peter Ochieng",
            phone="+254700000003",
            role=UserRole.driver,
            company_id=company.id,
        )
        driver3 = User(
            id="driver-003",
            email="mary.wanjiku@fueliq.ke",
            password_hash=hash_password("password123"),
            name="Mary Wanjiku",
            phone="+254700000004",
            role=UserRole.driver,
            company_id=company.id,
        )
        admin = User(
            id="admin-001",
            email="admin@fueliq.ke",
            password_hash=hash_password("admin123"),
            name="System Admin",
            phone="+254700000000",
            role=UserRole.admin,
            company_id=company.id,
        )

        for user in [manager, driver1, driver2, driver3, admin]:
            db.add(user)
        db.flush()

        # Vehicles
        vehicle1 = Vehicle(
            id="vehicle-001",
            registration_number="KCA 123A",
            make="Toyota",
            model="Hilux",
            year=2022,
            fuel_type=FuelType.diesel,
            tank_capacity_liters=80.0,
            odometer_km=45000.0,
            engine_size_l=2.4,
            cylinders=4,
            status=VehicleStatus.active,
            assigned_driver_id="driver-001",
            company_id=company.id,
        )
        vehicle2 = Vehicle(
            id="vehicle-002",
            registration_number="KCB 456B",
            make="Isuzu",
            model="D-Max",
            year=2021,
            fuel_type=FuelType.diesel,
            tank_capacity_liters=76.0,
            odometer_km=62000.0,
            engine_size_l=3.0,
            cylinders=4,
            status=VehicleStatus.active,
            assigned_driver_id="driver-002",
            company_id=company.id,
        )
        vehicle3 = Vehicle(
            id="vehicle-003",
            registration_number="KCC 789C",
            make="Mitsubishi",
            model="L200",
            year=2020,
            fuel_type=FuelType.diesel,
            tank_capacity_liters=75.0,
            odometer_km=85000.0,
            engine_size_l=2.4,
            cylinders=4,
            status=VehicleStatus.maintenance,
            company_id=company.id,
        )
        vehicle4 = Vehicle(
            id="vehicle-004",
            registration_number="KCD 012D",
            make="Toyota",
            model="Landcruiser",
            year=2023,
            fuel_type=FuelType.diesel,
            tank_capacity_liters=93.0,
            odometer_km=15000.0,
            engine_size_l=4.5,
            cylinders=6,
            status=VehicleStatus.inactive,
            company_id=company.id,
        )

        for v in [vehicle1, vehicle2, vehicle3, vehicle4]:
            db.add(v)
        db.flush()

        # Sample completed trips
        now = datetime.now(timezone.utc)
        trips_data = [
            {
                "id": "trip-001",
                "driver_id": "driver-001",
                "vehicle_id": "vehicle-001",
                "start_lat": -1.2921, "start_lng": 36.8219,  # Nairobi
                "end_lat": -1.5177, "end_lng": 37.2634,  # Machakos
                "distance_km": 65.3,
                "fuel_used_liters": 7.2,
                "fuel_efficiency": 9.07,
                "fuel_cost_kes": 1296.0,
                "avg_speed_kmh": 55.0,
                "max_speed_kmh": 95.0,
                "idle_time_minutes": 8.5,
                "route": "Nairobi - Machakos",
                "start_time": now - timedelta(days=2, hours=8),
                "end_time": now - timedelta(days=2, hours=6, minutes=50),
            },
            {
                "id": "trip-002",
                "driver_id": "driver-001",
                "vehicle_id": "vehicle-001",
                "start_lat": -1.5177, "start_lng": 37.2634,
                "end_lat": -1.2921, "end_lng": 36.8219,
                "distance_km": 67.1,
                "fuel_used_liters": 7.8,
                "fuel_efficiency": 8.60,
                "fuel_cost_kes": 1404.0,
                "avg_speed_kmh": 48.0,
                "max_speed_kmh": 88.0,
                "idle_time_minutes": 12.0,
                "route": "Machakos - Nairobi",
                "start_time": now - timedelta(days=2, hours=3),
                "end_time": now - timedelta(days=2, hours=1, minutes=35),
            },
            {
                "id": "trip-003",
                "driver_id": "driver-002",
                "vehicle_id": "vehicle-002",
                "start_lat": -1.2921, "start_lng": 36.8219,
                "end_lat": -0.0917, "end_lng": 34.7680,  # Kisumu
                "distance_km": 342.5,
                "fuel_used_liters": 38.0,
                "fuel_efficiency": 9.01,
                "fuel_cost_kes": 6840.0,
                "avg_speed_kmh": 72.0,
                "max_speed_kmh": 110.0,
                "idle_time_minutes": 25.0,
                "route": "Nairobi - Kisumu",
                "start_time": now - timedelta(days=5, hours=6),
                "end_time": now - timedelta(days=5, hours=1, minutes=15),
            },
            {
                "id": "trip-004",
                "driver_id": "driver-003",
                "vehicle_id": "vehicle-003",
                "start_lat": -1.2921, "start_lng": 36.8219,
                "end_lat": -4.0435, "end_lng": 39.6682,  # Mombasa
                "distance_km": 485.0,
                "fuel_used_liters": 48.5,
                "fuel_efficiency": 10.0,
                "fuel_cost_kes": 8730.0,
                "avg_speed_kmh": 68.0,
                "max_speed_kmh": 105.0,
                "idle_time_minutes": 35.0,
                "route": "Nairobi - Mombasa",
                "start_time": now - timedelta(days=7, hours=10),
                "end_time": now - timedelta(days=7, hours=3),
            },
            {
                "id": "trip-005",
                "driver_id": "driver-001",
                "vehicle_id": "vehicle-001",
                "start_lat": -1.2921, "start_lng": 36.8219,
                "end_lat": -1.1635, "end_lng": 36.9481,  # Thika
                "distance_km": 42.0,
                "fuel_used_liters": 4.8,
                "fuel_efficiency": 8.75,
                "fuel_cost_kes": 864.0,
                "avg_speed_kmh": 45.0,
                "max_speed_kmh": 80.0,
                "idle_time_minutes": 15.0,
                "route": "Nairobi - Thika",
                "start_time": now - timedelta(days=1, hours=5),
                "end_time": now - timedelta(days=1, hours=4, minutes=4),
            },
        ]

        for td in trips_data:
            trip = Trip(
                id=td["id"],
                driver_id=td["driver_id"],
                vehicle_id=td["vehicle_id"],
                company_id=company.id,
                start_latitude=td["start_lat"],
                start_longitude=td["start_lng"],
                start_location_timestamp=td["start_time"].isoformat(),
                end_latitude=td["end_lat"],
                end_longitude=td["end_lng"],
                end_location_timestamp=td["end_time"].isoformat(),
                start_time=td["start_time"],
                end_time=td["end_time"],
                status=TripStatus.completed,
                distance_km=td["distance_km"],
                fuel_used_liters=td["fuel_used_liters"],
                fuel_efficiency=td["fuel_efficiency"],
                fuel_cost_kes=td["fuel_cost_kes"],
                avg_speed_kmh=td["avg_speed_kmh"],
                max_speed_kmh=td["max_speed_kmh"],
                idle_time_minutes=td["idle_time_minutes"],
                route=td["route"],
            )
            db.add(trip)
        db.flush()

        # Recommendations
        recs = [
            Recommendation(
                company_id=company.id,
                type=RecommendationType.fuel_saving,
                title="Reduce Idling Time",
                description="Vehicles KCA 123A and KCB 456B show excessive idling. Reducing idle time by 50% could save approximately 15 liters of fuel per month.",
                priority=Priority.high,
                potential_savings_kes=2700.0,
                affected_vehicles=json.dumps(["KCA 123A", "KCB 456B"]),
            ),
            Recommendation(
                company_id=company.id,
                type=RecommendationType.maintenance,
                title="Schedule Service for KCC 789C",
                description="Vehicle KCC 789C fuel efficiency has dropped by 12% over the last month. A maintenance check is recommended.",
                priority=Priority.high,
                potential_savings_kes=5400.0,
                affected_vehicles=json.dumps(["KCC 789C"]),
            ),
            Recommendation(
                company_id=company.id,
                type=RecommendationType.route_optimization,
                title="Alternative Route: Nairobi-Machakos",
                description="Using the Mombasa Road exit instead of Kangundo Road can reduce the Nairobi-Machakos trip distance by 8km, saving approximately 150 liters monthly across the fleet.",
                priority=Priority.medium,
                potential_savings_kes=27000.0,
            ),
            Recommendation(
                company_id=company.id,
                type=RecommendationType.driving_behavior,
                title="Eco-Driving Training",
                description="Implementing eco-driving training for all drivers could improve fleet fuel efficiency by 8-10%.",
                priority=Priority.medium,
                potential_savings_kes=45000.0,
            ),
        ]
        for r in recs:
            db.add(r)

        # Budgets
        budgets = [
            Budget(
                company_id=company.id,
                route_id="route-nbi-mks",
                route_name="Nairobi - Machakos",
                monthly_budget_kes=50000.0,
            ),
            Budget(
                company_id=company.id,
                route_id="route-nbi-ksm",
                route_name="Nairobi - Kisumu",
                monthly_budget_kes=150000.0,
            ),
            Budget(
                company_id=company.id,
                route_id="route-nbi-msa",
                route_name="Nairobi - Mombasa",
                monthly_budget_kes=200000.0,
            ),
        ]
        for b in budgets:
            db.add(b)

        db.commit()
        print("Database seeded successfully!")
        print("  - 1 company: Safari Logistics Ltd")
        print("  - 5 users: manager@fueliq.ke, driver@fueliq.ke, peter.ochieng@fueliq.ke, mary.wanjiku@fueliq.ke, admin@fueliq.ke")
        print("  - 4 vehicles: KCA 123A, KCB 456B, KCC 789C, KCD 012D")
        print("  - 5 completed trips")
        print("  - 4 recommendations")
        print("  - 3 route budgets")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
