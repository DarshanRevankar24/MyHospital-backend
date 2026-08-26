"""Hospital service API routes."""

from typing import Any

from fastapi import APIRouter, Query
from fastcrud import compute_offset

from ...infrastructure.auth.http_exceptions import HTTPException
from ...infrastructure.dependencies import AsyncSessionDep, CurrentSuperUserDep, CurrentUserDep
from ..common.utils.error_handler import handle_exception
from .dependencies import HospitalServiceDep
from .schemas import HospitalBookingCreate, HospitalDoctorCreate, HospitalProviderCreate

router = APIRouter(tags=["Services — Hospital"])


# ── Providers (public browse) ─────────────────────────────────────────────────


@router.get(
    "/",
    summary="List Hospitals",
    description="Browse verified hospitals. Filter by city or speciality.",
)
async def list_hospitals(
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
    city: str | None = Query(default=None),
    speciality: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=10, ge=1, le=50),
) -> dict[str, Any]:
    try:
        skip = compute_offset(page, items_per_page)
        return await hospital_service.list_providers(db=db, city=city, speciality=speciality, skip=skip, limit=items_per_page)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{provider_id}", summary="Get Hospital Detail")
async def get_hospital(
    provider_id: int,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
) -> dict[str, Any]:
    try:
        return await hospital_service.get_provider(provider_id, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{provider_id}/doctors", summary="List Doctors at Hospital")
async def list_doctors(
    provider_id: int,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
    speciality: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        return await hospital_service.list_doctors(provider_id, db, speciality=speciality)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{provider_id}/doctors/{doctor_id}/slots", summary="Get Available Appointment Slots")
async def list_slots(
    provider_id: int,
    doctor_id: int,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
    slot_date: str | None = Query(default=None, description="Date in YYYY-MM-DD format"),
) -> dict[str, Any]:
    try:
        return await hospital_service.list_slots(provider_id, doctor_id, slot_date, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# ── Bookings (user auth) ──────────────────────────────────────────────────────


@router.post("/bookings", summary="Book Hospital Appointment", status_code=201)
async def create_booking(
    data: HospitalBookingCreate,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
) -> dict[str, Any]:
    try:
        return await hospital_service.create_booking(current_user["id"], data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/bookings", summary="My Hospital Bookings")
async def list_my_bookings(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
) -> dict[str, Any]:
    try:
        return await hospital_service.list_user_bookings(current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/bookings/{booking_id}", summary="Get Booking Detail")
async def get_booking(
    booking_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
) -> dict[str, Any]:
    try:
        return await hospital_service.get_booking(booking_id, current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/bookings/{booking_id}", summary="Cancel Hospital Booking")
async def cancel_booking(
    booking_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
) -> dict[str, str]:
    try:
        await hospital_service.cancel_booking(booking_id, current_user["id"], db)
        return {"message": "Booking cancelled successfully"}
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# ── Admin seed endpoints ──────────────────────────────────────────────────────


@router.post("/admin/providers", summary="[Admin] Add Hospital Provider", status_code=201)
async def create_provider(
    data: HospitalProviderCreate,
    _: CurrentSuperUserDep,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
) -> dict[str, Any]:
    try:
        return await hospital_service.create_provider(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/admin/doctors", summary="[Admin] Add Doctor", status_code=201)
async def create_doctor(
    data: HospitalDoctorCreate,
    _: CurrentSuperUserDep,
    db: AsyncSessionDep,
    hospital_service: HospitalServiceDep,
) -> dict[str, Any]:
    try:
        return await hospital_service.create_doctor(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
