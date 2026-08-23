"""Laboratory service API routes."""

from typing import Any
from fastapi import APIRouter, Query
from ....infrastructure.dependencies import AsyncSessionDep, CurrentSuperUserDep, CurrentUserDep
from ...common.utils.error_handler import handle_exception
from ....infrastructure.auth.http_exceptions import HTTPException
from .dependencies import LaboratoryServiceDep
from .schemas import LabBookingCreate, LabTestCreate, LaboratoryProviderCreate

router = APIRouter(tags=["Services — Laboratory"])


@router.get("/", summary="List Laboratories")
async def list_labs(
    db: AsyncSessionDep, lab_service: LaboratoryServiceDep,
    city: str | None = Query(default=None),
    home_collection: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=10, ge=1, le=50),
) -> dict[str, Any]:
    try:
        from fastcrud import compute_offset
        return await lab_service.list_providers(db=db, city=city, home_collection=home_collection,
                                                 skip=compute_offset(page, items_per_page), limit=items_per_page)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{provider_id}", summary="Get Laboratory Detail")
async def get_lab(provider_id: int, db: AsyncSessionDep, lab_service: LaboratoryServiceDep) -> dict[str, Any]:
    try:
        return await lab_service.get_provider(provider_id, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{provider_id}/tests", summary="List Lab Tests")
async def list_tests(
    provider_id: int, db: AsyncSessionDep, lab_service: LaboratoryServiceDep,
    category: str | None = Query(default=None),
) -> dict[str, Any]:
    try:
        return await lab_service.list_tests(provider_id, db, category=category)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/tests/search", summary="Search Tests Across Labs")
async def search_tests(
    db: AsyncSessionDep, lab_service: LaboratoryServiceDep,
    name: str = Query(min_length=2),
) -> dict[str, Any]:
    try:
        return await lab_service.search_tests(db, name)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/bookings", summary="Book Lab Tests", status_code=201)
async def create_booking(
    data: LabBookingCreate, current_user: CurrentUserDep,
    db: AsyncSessionDep, lab_service: LaboratoryServiceDep,
) -> dict[str, Any]:
    try:
        return await lab_service.create_booking(current_user["id"], data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/bookings", summary="My Lab Bookings")
async def list_my_bookings(current_user: CurrentUserDep, db: AsyncSessionDep,
                            lab_service: LaboratoryServiceDep) -> dict[str, Any]:
    try:
        return await lab_service.list_user_bookings(current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/bookings/{booking_id}", summary="Get Lab Booking Detail")
async def get_booking(booking_id: int, current_user: CurrentUserDep, db: AsyncSessionDep,
                       lab_service: LaboratoryServiceDep) -> dict[str, Any]:
    try:
        return await lab_service.get_booking(booking_id, current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/bookings/{booking_id}", summary="Cancel Lab Booking")
async def cancel_booking(booking_id: int, current_user: CurrentUserDep, db: AsyncSessionDep,
                          lab_service: LaboratoryServiceDep) -> dict[str, str]:
    try:
        await lab_service.cancel_booking(booking_id, current_user["id"], db)
        return {"message": "Booking cancelled"}
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/admin/providers", summary="[Admin] Add Lab", status_code=201)
async def create_provider(_: CurrentSuperUserDep, data: LaboratoryProviderCreate,
                           db: AsyncSessionDep, lab_service: LaboratoryServiceDep) -> dict[str, Any]:
    try:
        return await lab_service.create_provider(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/admin/tests", summary="[Admin] Add Lab Test", status_code=201)
async def create_test(_: CurrentSuperUserDep, data: LabTestCreate,
                       db: AsyncSessionDep, lab_service: LaboratoryServiceDep) -> dict[str, Any]:
    try:
        return await lab_service.create_test(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
