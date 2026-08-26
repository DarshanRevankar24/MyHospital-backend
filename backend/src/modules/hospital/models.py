"""Hospital module SQLAlchemy models."""

from datetime import date, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base


class HospitalProvider(Base, TimestampMixin):
    """A hospital or clinic offering consultations."""

    __tablename__ = "hospital_provider"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(120))
    registration_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    address_line1: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(60), index=True)
    state: Mapped[str] = mapped_column(String(60))
    pincode: Mapped[str] = mapped_column(String(10))
    phone: Mapped[str] = mapped_column(String(15))

    address_line2: Mapped[str | None] = mapped_column(String(120), default=None)
    email: Mapped[str | None] = mapped_column(String(80), default=None)
    website: Mapped[str | None] = mapped_column(String(200), default=None)
    specialities: Mapped[list] = mapped_column(JSON, default=list)
    is_emergency_available: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    logo_url: Mapped[str | None] = mapped_column(String(300), default=None)

    doctors: Mapped[list["HospitalDoctor"]] = relationship(
        "HospitalDoctor", back_populates="provider", lazy="selectin", init=False
    )

    def __repr__(self) -> str:
        return f"HospitalProvider({self.name}, {self.city})"


class HospitalDoctor(Base, TimestampMixin):
    """A doctor belonging to a hospital provider."""

    __tablename__ = "hospital_doctor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospital_provider.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    speciality: Mapped[str] = mapped_column(String(60))
    qualification: Mapped[str] = mapped_column(String(120))
    consultation_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    available_days: Mapped[list] = mapped_column(JSON, default=list)
    slot_duration_min: Mapped[int] = mapped_column(Integer, default=15)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    provider: Mapped["HospitalProvider"] = relationship(
        "HospitalProvider", back_populates="doctors", lazy="selectin", init=False
    )
    slots: Mapped[list["HospitalSlot"]] = relationship("HospitalSlot", back_populates="doctor", lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"Dr. {self.name} ({self.speciality})"


class HospitalSlot(Base, TimestampMixin):
    """An available appointment slot for a doctor."""

    __tablename__ = "hospital_slot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospital_provider.id"), index=True)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospital_doctor.id"), index=True)
    slot_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    total_capacity: Mapped[int] = mapped_column(Integer, default=1)
    booked_count: Mapped[int] = mapped_column(Integer, default=0)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    doctor: Mapped["HospitalDoctor"] = relationship("HospitalDoctor", back_populates="slots", lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"HospitalSlot({self.slot_date} {self.start_time})"


class HospitalBooking(Base, TimestampMixin):
    """A user's appointment booking at a hospital."""

    __tablename__ = "hospital_booking"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    booking_ref: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospital_provider.id"), index=True)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospital_doctor.id"), index=True)
    slot_id: Mapped[int] = mapped_column(Integer, ForeignKey("hospital_slot.id"), index=True)
    patient_name: Mapped[str] = mapped_column(String(80))
    patient_phone: Mapped[str] = mapped_column(String(15))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    patient_dob: Mapped[date | None] = mapped_column(Date, default=None)
    patient_gender: Mapped[str | None] = mapped_column(String(10), default=None)
    symptoms: Mapped[str | None] = mapped_column(String(500), default=None)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    def __repr__(self) -> str:
        return f"HospitalBooking({self.booking_ref}, {self.status})"
