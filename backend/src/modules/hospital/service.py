"""Hospital module service layer."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceNotFoundError, ValidationError
from .crud import crud_hospital_bookings, crud_hospital_doctors, crud_hospital_providers, crud_hospital_slots
from .schemas import (
    HospitalBookingCreate, HospitalBookingCreateInternal,
    HospitalBookingRead,
    HospitalDoctorCreate,
    HospitalDoctorRead,
    HospitalProviderCreate,
    HospitalProviderRead,
    HospitalSlotCreate,
    HospitalSlotRead,
)


def _generate_booking_ref() -> str:
    """Generate a short unique booking reference like MH-HSP-XXXX."""
    short = uuid.uuid4().hex[:8].upper()
    return f"MH-HSP-{short}"


class HospitalService:
    """Business logic for hospital consultancy bookings."""

    # ── Providers ──────────────────────────────────────────────────────────

    async def list_providers(
        self,
        db: AsyncSession,
        city: str | None = None,
        speciality: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> dict[str, Any]:
        filters: dict[str, Any] = {"is_active": True, "is_verified": True}
        if city:
            filters["city"] = city
        res = await crud_hospital_providers.get_multi(
            db=db, offset=skip, limit=limit, schema_to_select=HospitalProviderRead, **filters
        )
        return dict(res)

    async def get_provider(self, provider_id: int, db: AsyncSession) -> dict[str, Any]:
        provider = await crud_hospital_providers.get(
            db=db, id=provider_id, is_active=True, schema_to_select=HospitalProviderRead
        )
        if not provider:
            raise ResourceNotFoundError(f"Hospital provider {provider_id} not found")
        return dict(provider)

    async def create_provider(self, data: HospitalProviderCreate, db: AsyncSession) -> dict[str, Any]:
        existing = await crud_hospital_providers.exists(db=db, registration_number=data.registration_number)
        if existing:
            raise ValidationError("A provider with this registration number already exists")
        created = await crud_hospital_providers.create(db=db, object=data, schema_to_select=HospitalProviderRead)
        if not created:
            raise ValidationError("Failed to create provider")
        return dict(created)

    # ── Doctors ────────────────────────────────────────────────────────────

    async def list_doctors(self, provider_id: int, db: AsyncSession, speciality: str | None = None) -> dict[str, Any]:
        await self.get_provider(provider_id, db)
        filters: dict[str, Any] = {"provider_id": provider_id, "is_active": True}
        if speciality:
            filters["speciality"] = speciality
        res = await crud_hospital_doctors.get_multi(db=db, offset=0, limit=100, schema_to_select=HospitalDoctorRead, **filters)
        return dict(res)

    async def create_doctor(self, data: HospitalDoctorCreate, db: AsyncSession) -> dict[str, Any]:
        await self.get_provider(data.provider_id, db)
        created = await crud_hospital_doctors.create(db=db, object=data, schema_to_select=HospitalDoctorRead)
        if not created:
            raise ValidationError("Failed to create doctor")
        return dict(created)

    # ── Slots ──────────────────────────────────────────────────────────────

    async def list_slots(self, provider_id: int, doctor_id: int, slot_date: str | None, db: AsyncSession) -> dict[str, Any]:
        filters: dict[str, Any] = {
            "provider_id": provider_id,
            "doctor_id": doctor_id,
            "is_blocked": False,
        }
        if slot_date:
            filters["slot_date"] = slot_date
        res = await crud_hospital_slots.get_multi(db=db, offset=0, limit=100, schema_to_select=HospitalSlotRead, **filters)
        return dict(res)

    async def create_slot(self, data: HospitalSlotCreate, db: AsyncSession) -> dict[str, Any]:
        created = await crud_hospital_slots.create(db=db, object=data, schema_to_select=HospitalSlotRead)
        if not created:
            raise ValidationError("Failed to create slot")
        return dict(created)

    # ── Bookings ───────────────────────────────────────────────────────────

    async def create_booking(self, user_id: int, data: HospitalBookingCreate, db: AsyncSession) -> dict[str, Any]:
        # Validate slot
        slot = await crud_hospital_slots.get(db=db, id=data.slot_id, is_blocked=False)
        if not slot:
            raise ResourceNotFoundError("Slot not found or blocked")
        if slot["booked_count"] >= slot["total_capacity"]:
            raise ValidationError("This slot is fully booked")

        # Get doctor fee
        doctor = await crud_hospital_doctors.get(db=db, id=data.doctor_id, is_active=True)
        if not doctor:
            raise ResourceNotFoundError("Doctor not found")

        booking_data = {
            "booking_ref": _generate_booking_ref(),
            "user_id": user_id,
            "provider_id": data.provider_id,
            "doctor_id": data.doctor_id,
            "slot_id": data.slot_id,
            "patient_name": data.patient_name,
            "patient_dob": data.patient_dob,
            "patient_gender": data.patient_gender,
            "patient_phone": data.patient_phone,
            "symptoms": data.symptoms,
            "status": "pending",
            "amount": doctor["consultation_fee"],
        }

        # Atomically increment slot booked_count
        await crud_hospital_slots.update(
            db=db,
            object={"booked_count": slot["booked_count"] + 1},
            id=data.slot_id,
        )

        created = await crud_hospital_bookings.create(db=db, object=HospitalBookingCreateInternal(**booking_data), schema_to_select=HospitalBookingRead)
        if not created:
            raise ValidationError("Failed to create booking")
        return dict(created)

    async def list_user_bookings(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        res = await crud_hospital_bookings.get_multi(
            db=db, offset=0, limit=50, schema_to_select=HospitalBookingRead, user_id=user_id
        )
        return dict(res)

    async def get_booking(self, booking_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        booking = await crud_hospital_bookings.get(db=db, id=booking_id, user_id=user_id, schema_to_select=HospitalBookingRead)
        if not booking:
            raise ResourceNotFoundError("Booking not found")
        return dict(booking)

    async def cancel_booking(self, booking_id: int, user_id: int, db: AsyncSession) -> None:
        booking = await crud_hospital_bookings.get(db=db, id=booking_id, user_id=user_id)
        if not booking:
            raise ResourceNotFoundError("Booking not found")
        if booking["status"] not in ("pending", "confirmed"):
            raise ValidationError("Only pending or confirmed bookings can be cancelled")

        await crud_hospital_bookings.update(db=db, object={"status": "cancelled"}, id=booking_id)
        # Release slot
        slot = await crud_hospital_slots.get(db=db, id=booking["slot_id"])
        if slot and slot["booked_count"] > 0:
            await crud_hospital_slots.update(db=db, object={"booked_count": slot["booked_count"] - 1}, id=booking["slot_id"])
