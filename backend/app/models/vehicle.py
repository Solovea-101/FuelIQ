import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class VehicleStatus(str, enum.Enum):
    active = "active"
    maintenance = "maintenance"
    inactive = "inactive"


class FuelType(str, enum.Enum):
    petrol = "petrol"
    diesel = "diesel"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    registration_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    fuel_type: Mapped[FuelType] = mapped_column(SAEnum(FuelType), nullable=False)
    tank_capacity_liters: Mapped[float] = mapped_column(Float, nullable=False)
    odometer_km: Mapped[float] = mapped_column(Float, default=0.0)
    engine_size_l: Mapped[float | None] = mapped_column(Float, nullable=True)
    cylinders: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[VehicleStatus] = mapped_column(SAEnum(VehicleStatus), default=VehicleStatus.active)
    assigned_driver_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)
    last_service_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    next_service_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    company = relationship("Company", back_populates="vehicles")
    assigned_driver = relationship("User", back_populates="assigned_vehicle", foreign_keys=[assigned_driver_id])
    trips = relationship("Trip", back_populates="vehicle")
