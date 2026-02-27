import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class TripStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    vehicle_id: Mapped[str] = mapped_column(String(36), ForeignKey("vehicles.id"), nullable=False)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)

    # Location fields (stored as JSON-like strings for start/end)
    start_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    start_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    start_altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_location_timestamp: Mapped[str | None] = mapped_column(String(50), nullable=True)

    end_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_location_timestamp: Mapped[str | None] = mapped_column(String(50), nullable=True)

    start_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[TripStatus] = mapped_column(SAEnum(TripStatus), default=TripStatus.in_progress)

    # Metrics
    distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    fuel_used_liters: Mapped[float | None] = mapped_column(Float, nullable=True)
    fuel_efficiency: Mapped[float | None] = mapped_column(Float, nullable=True)
    fuel_cost_kes: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    idle_time_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ML fields
    predicted_fuel_liters: Mapped[float | None] = mapped_column(Float, nullable=True)
    efficiency_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    route: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    driver = relationship("User", back_populates="trips", foreign_keys=[driver_id])
    vehicle = relationship("Vehicle", back_populates="trips")
    company = relationship("Company", back_populates="trips")
    waypoints = relationship("GPSWaypoint", back_populates="trip", order_by="GPSWaypoint.sequence_order")


class GPSWaypoint(Base):
    __tablename__ = "gps_waypoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id"), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)

    trip = relationship("Trip", back_populates="waypoints")
