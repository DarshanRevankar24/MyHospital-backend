"""Ambulance API routes."""

from typing import Any

from fastapi import APIRouter, Query
from fastcrud import compute_offset

from ...infrastructure.auth.http_exceptions import HTTPException
from ...infrastructure.dependencies import AsyncSessionDep, CurrentSuperUserDep, CurrentUserDep
from ..common.utils.error_handler import handle_exception
from .dependencies import AmbulanceServiceDep
from .schemas import AmbulanceProviderCreate, AmbulanceRequestCreate, AmbulanceVehicleCreate

router = APIRouter(tags=["Services — Ambulance"])


@router.get("/", summary="List Ambulance Providers")
async def list_providers(
    db: AsyncSessionDep,
    service: AmbulanceServiceDep,
    city: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=10, ge=1, le=50),
) -> dict[str, Any]:
    try:
        return await service.list_providers(db=db, city=city, skip=compute_offset(page, items_per_page), limit=items_per_page)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/available", summary="Find Available Ambulances")
async def find_available(
    db: AsyncSessionDep, service: AmbulanceServiceDep, city: str | None = Query(default=None)
) -> dict[str, Any]:
    try:
        return await service.list_available_vehicles(db=db, city=city)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/requests", summary="Request Ambulance", status_code=201)
async def create_request(
    data: AmbulanceRequestCreate, current_user: CurrentUserDep, db: AsyncSessionDep, service: AmbulanceServiceDep
) -> dict[str, Any]:
    try:
        return await service.create_request(current_user["id"], data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/requests", summary="My Ambulance Requests")
async def list_my_requests(current_user: CurrentUserDep, db: AsyncSessionDep, service: AmbulanceServiceDep) -> dict[str, Any]:
    try:
        return await service.list_user_requests(current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/requests/{request_id}", summary="Ambulance Request Detail")
async def get_request(
    request_id: int, current_user: CurrentUserDep, db: AsyncSessionDep, service: AmbulanceServiceDep
) -> dict[str, Any]:
    try:
        return await service.get_request(request_id, current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/requests/{request_id}", summary="Cancel Ambulance Request")
async def cancel_request(
    request_id: int, current_user: CurrentUserDep, db: AsyncSessionDep, service: AmbulanceServiceDep
) -> dict[str, str]:
    try:
        await service.cancel_request(request_id, current_user["id"], db)
        return {"message": "Request cancelled"}
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/admin/providers", summary="[Admin] Add Ambulance Provider", status_code=201)
async def create_provider(
    _: CurrentSuperUserDep, data: AmbulanceProviderCreate, db: AsyncSessionDep, service: AmbulanceServiceDep
) -> dict[str, Any]:
    try:
        return await service.create_provider(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/admin/vehicles", summary="[Admin] Add Ambulance Vehicle", status_code=201)
async def create_vehicle(
    _: CurrentSuperUserDep, data: AmbulanceVehicleCreate, db: AsyncSessionDep, service: AmbulanceServiceDep
) -> dict[str, Any]:
    try:
        return await service.create_vehicle(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
