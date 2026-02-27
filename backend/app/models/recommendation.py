import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Float, Boolean, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class RecommendationType(str, enum.Enum):
    fuel_saving = "fuel_saving"
    maintenance = "maintenance"
    route_optimization = "route_optimization"
    driving_behavior = "driving_behavior"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)
    type: Mapped[RecommendationType] = mapped_column(SAEnum(RecommendationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[Priority] = mapped_column(SAEnum(Priority), nullable=False)
    potential_savings_kes: Mapped[float | None] = mapped_column(Float, nullable=True)
    affected_vehicles: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as string
    affected_drivers: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as string
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    company = relationship("Company", back_populates="recommendations")
