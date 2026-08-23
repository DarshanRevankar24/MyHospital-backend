"""Pharmacy API routes."""

from typing import Any
from fastapi import APIRouter, Query
from ...infrastructure.dependencies import AsyncSessionDep, CurrentSuperUserDep, CurrentUserDep
from ..common.utils.error_handler import handle_exception
from ...infrastructure.auth.http_exceptions import HTTPException
from .dependencies import PharmacyServiceDep
from .schemas import MedicineCreate, PharmacyOrderCreate, PharmacyProviderCreate

router = APIRouter(tags=["Services — Pharmacy"])

@router.get("/", summary="List Pharmacies")
async def list_pharmacies(db: AsyncSessionDep, service: PharmacyServiceDep,
                          city: str | None = Query(default=None),
                          delivery: bool | None = Query(default=None),
                          page: int = Query(default=1, ge=1),
                          items_per_page: int = Query(default=10, ge=1, le=50)) -> dict[str, Any]:
    try:
        from fastcrud import compute_offset
        return await service.list_providers(db=db, city=city, delivery=delivery,
                                            skip=compute_offset(page, items_per_page), limit=items_per_page)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/{provider_id}", summary="Get Pharmacy Detail")
async def get_pharmacy(provider_id: int, db: AsyncSessionDep, service: PharmacyServiceDep) -> dict[str, Any]:
    try:
        return await service.get_provider(provider_id, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/{provider_id}/medicines", summary="List Medicines at Pharmacy")
async def list_medicines(provider_id: int, db: AsyncSessionDep, service: PharmacyServiceDep,
                         category: str | None = Query(default=None)) -> dict[str, Any]:
    try:
        return await service.list_medicines(provider_id, db, category=category)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/medicines/search", summary="Search Medicines Across All Pharmacies")
async def search_medicines(name: str = Query(min_length=2), db: AsyncSessionDep = None,
                           service: PharmacyServiceDep = None) -> dict[str, Any]:
    try:
        return await service.search_medicines(db, name)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/orders", summary="Place Pharmacy Order", status_code=201)
async def create_order(data: PharmacyOrderCreate, current_user: CurrentUserDep,
                       db: AsyncSessionDep, service: PharmacyServiceDep) -> dict[str, Any]:
    try:
        return await service.create_order(current_user["id"], data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/orders", summary="My Pharmacy Orders")
async def list_my_orders(current_user: CurrentUserDep, db: AsyncSessionDep,
                         service: PharmacyServiceDep) -> dict[str, Any]:
    try:
        return await service.list_user_orders(current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/orders/{order_id}", summary="Pharmacy Order Detail")
async def get_order(order_id: int, current_user: CurrentUserDep, db: AsyncSessionDep,
                    service: PharmacyServiceDep) -> dict[str, Any]:
    try:
        return await service.get_order(order_id, current_user["id"], db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete("/orders/{order_id}", summary="Cancel Pharmacy Order")
async def cancel_order(order_id: int, current_user: CurrentUserDep, db: AsyncSessionDep,
                       service: PharmacyServiceDep) -> dict[str, str]:
    try:
        await service.cancel_order(order_id, current_user["id"], db)
        return {"message": "Order cancelled"}
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/admin/providers", summary="[Admin] Add Pharmacy", status_code=201)
async def create_provider(_: CurrentSuperUserDep, data: PharmacyProviderCreate,
                          db: AsyncSessionDep, service: PharmacyServiceDep) -> dict[str, Any]:
    try:
        return await service.create_provider(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/admin/medicines", summary="[Admin] Add Medicine", status_code=201)
async def create_medicine(_: CurrentSuperUserDep, data: MedicineCreate,
                          db: AsyncSessionDep, service: PharmacyServiceDep) -> dict[str, Any]:
    try:
        return await service.create_medicine(data, db)
    except Exception as e:
        exc = handle_exception(e)
        if exc: raise exc
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
