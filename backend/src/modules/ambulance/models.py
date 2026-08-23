"""Ambulance SQLAlchemy models."""

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base


class AmbulanceProvider(Base, TimestampMixin):
    __tablename__ = "ambulance_provider"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(120))
    registration_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    city: Mapped[str] = mapped_column(String(60), index=True)
    state: Mapped[str] = mapped_column(String(60))
    phone: Mapped[str] = mapped_column(String(15))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    vehicles: Mapped[list["AmbulanceVehicle"]] = relationship("AmbulanceVehicle", back_populates="provider", lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"AmbulanceProvider({self.name})"


class AmbulanceVehicle(Base, TimestampMixin):
    __tablename__ = "ambulance_vehicle"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("ambulance_provider.id"), index=True)
    vehicle_number: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ambulance_type: Mapped[str] = mapped_column(String(30), index=True)
    is_ac: Mapped[bool] = mapped_column(Boolean, default=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    provider: Mapped["AmbulanceProvider"] = relationship("AmbulanceProvider", back_populates="vehicles", lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"AmbulanceVehicle({self.vehicle_number}, {self.ambulance_type})"


class AmbulanceRequest(Base, TimestampMixin):
    __tablename__ = "ambulance_request"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    request_ref: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    pickup_address: Mapped[str] = mapped_column(String(300))
    destination_address: Mapped[str] = mapped_column(String(300))
    patient_name: Mapped[str] = mapped_column(String(80))
    ambulance_type: Mapped[str] = mapped_column(String(30))
    
    provider_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ambulance_provider.id"), index=True, default=None)
    vehicle_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("ambulance_vehicle.id"), index=True, default=None)
    pickup_latitude: Mapped[float | None] = mapped_column(Float, default=None)
    pickup_longitude: Mapped[float | None] = mapped_column(Float, default=None)
    patient_condition: Mapped[str | None] = mapped_column(String(300), default=None)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    assigned_at: Mapped[str | None] = mapped_column(String(30), default=None)
    estimated_arrival_min: Mapped[int | None] = mapped_column(Integer, default=None)

    def __repr__(self) -> str:
        return f"AmbulanceRequest({self.request_ref}, {self.status})"
