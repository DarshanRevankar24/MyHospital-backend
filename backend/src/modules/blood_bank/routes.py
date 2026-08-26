"""Blood Bank API routes."""

from typing import Any

from fastapi import APIRouter, Query
from fastcrud import compute_offset

from ...infrastructure.auth.http_exceptions import HTTPException
from ...infrastructure.dependencies import AsyncSessionDep, CurrentSuperUserDep, CurrentUserDep
from ..common.utils.error_handler import handle_exception
from .dependencies import BloodBankServiceDep
from .schemas import BloodBankProviderCreate, BloodRequestCreate, BloodStockCreate

router = APIRouter(tags=["Services — Blood Bank"])


@router.get("/", summary="List Blood Banks")
async def list_blood_banks(
    db: AsyncSessionDep,
    service: BloodBankServiceDep,
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


@router.get("/{provider_id}", summary="Get Blood Bank Detail")
async def get_blood_bank(provider_id: int, db: AsyncSessionDep, service: BloodBankServiceDep) -> dict[str, Any]:
    try:
        return await service.get_provider(provider_id, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{provider_id}/stock", summary="Blood Stock Availability")
async def get_stock(provider_id: int, db: AsyncSessionDep, service: BloodBankServiceDep) -> dict[str, Any]:
    try:
        return await service.get_stock(provider_id, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/stock/search", summary="Find Blood Group Across All Banks")
async def search_stock(
    db: AsyncSessionDep, service: BloodBankServiceDep, blood_group: str = Query(min_length=1)
) -> dict[str, Any]:
    try:
        return await service.search_blood_group(blood_group, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/requests", summary="Request Blood Units", status_code=201)
async def create_request(
    data: BloodRequestCreate, current_user: CurrentUserDep, db: AsyncSessionDep, service: BloodBankServiceDep
) -> dict[str, Any]:
    try:
        return await service.create_request(current_user["id"], data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/requests", summary="My Blood Requests")
async def list_my_requests(current_user: CurrentUserDep, db: AsyncSessionDep, service: BloodBankServiceDep) -> dict[str, Any]:
    try:
        return await service.list_user_requests(current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/requests/{request_id}", summary="Blood Request Detail")
async def get_request(
    request_id: int, current_user: CurrentUserDep, db: AsyncSessionDep, service: BloodBankServiceDep
) -> dict[str, Any]:
    try:
        return await service.get_request(request_id, current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/requests/{request_id}", summary="Cancel Blood Request")
async def cancel_request(
    request_id: int, current_user: CurrentUserDep, db: AsyncSessionDep, service: BloodBankServiceDep
) -> dict[str, str]:
    try:
        await service.cancel_request(request_id, current_user["id"], db)
        return {"message": "Request cancelled"}
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/admin/providers", summary="[Admin] Add Blood Bank", status_code=201)
async def create_provider(
    _: CurrentSuperUserDep, data: BloodBankProviderCreate, db: AsyncSessionDep, service: BloodBankServiceDep
) -> dict[str, Any]:
    try:
        return await service.create_provider(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/admin/stock", summary="[Admin] Set Blood Stock", status_code=201)
async def upsert_stock(
    _: CurrentSuperUserDep, data: BloodStockCreate, db: AsyncSessionDep, service: BloodBankServiceDep
) -> dict[str, Any]:
    try:
        return await service.upsert_stock(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
