"""Hospital module Pydantic schemas."""

from datetime import date, time
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .enums import BookingStatus, Speciality

# ── Provider ──────────────────────────────────────────────────────────────────


class HospitalProviderRead(BaseModel):
    """Public-facing hospital provider detail."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    registration_number: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    pincode: str
    phone: str
    email: str | None = None
    website: str | None = None
    specialities: list[str] = []
    is_emergency_available: bool
    is_verified: bool
    logo_url: str | None = None


class HospitalProviderCreate(BaseModel):
    """Admin-only: create a hospital provider (seed data)."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=2, max_length=120)]
    registration_number: Annotated[str, Field(min_length=2, max_length=60)]
    address_line1: Annotated[str, Field(min_length=2, max_length=120)]
    address_line2: str | None = None
    city: Annotated[str, Field(min_length=2, max_length=60)]
    state: Annotated[str, Field(min_length=2, max_length=60)]
    pincode: Annotated[str, Field(pattern=r"^\d{6}$")]
    phone: Annotated[str, Field(min_length=10, max_length=15)]
    email: str | None = None
    website: str | None = None
    specialities: list[Speciality] = []
    is_emergency_available: bool = False
    logo_url: str | None = None


# ── Doctor ────────────────────────────────────────────────────────────────────


class HospitalDoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    name: str
    speciality: str
    qualification: str
    experience_years: int
    consultation_fee: Decimal
    available_days: list[str]
    slot_duration_min: int
    is_active: bool


class HospitalDoctorCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int
    name: Annotated[str, Field(min_length=2, max_length=80)]
    speciality: Speciality
    qualification: Annotated[str, Field(min_length=2, max_length=120)]
    experience_years: Annotated[int, Field(ge=0, le=60)]
    consultation_fee: Annotated[Decimal, Field(gt=0)]
    available_days: list[str] = []
    slot_duration_min: Annotated[int, Field(ge=5, le=120, default=15)]


# ── Slot ──────────────────────────────────────────────────────────────────────


class HospitalSlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    doctor_id: int
    slot_date: date
    start_time: time
    end_time: time
    total_capacity: int
    booked_count: int
    is_blocked: bool

    @property
    def is_available(self) -> bool:
        return not self.is_blocked and self.booked_count < self.total_capacity


class HospitalSlotCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int
    doctor_id: int
    slot_date: date
    start_time: time
    end_time: time
    total_capacity: Annotated[int, Field(ge=1, default=1)]


# ── Booking ───────────────────────────────────────────────────────────────────


class HospitalBookingCreate(BaseModel):
    """User creates a hospital booking."""

    model_config = ConfigDict(extra="forbid")

    provider_id: int
    doctor_id: int
    slot_id: int
    patient_name: Annotated[str, Field(min_length=2, max_length=80)]
    patient_dob: date | None = None
    patient_gender: str | None = None
    patient_phone: Annotated[str, Field(min_length=10, max_length=15)]
    symptoms: Annotated[str | None, Field(max_length=500, default=None)]


class HospitalBookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_ref: str
    user_id: int
    provider_id: int
    doctor_id: int
    slot_id: int
    patient_name: str
    patient_dob: date | None = None
    patient_gender: str | None = None
    patient_phone: str
    symptoms: str | None = None
    status: BookingStatus
    amount: Decimal
