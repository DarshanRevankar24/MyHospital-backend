"""Ambulance service layer."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceNotFoundError, ValidationError
from .crud import crud_ambulance_providers, crud_ambulance_requests, crud_ambulance_vehicles
from .schemas import (
    AmbulanceProviderCreate,
    AmbulanceProviderRead,
    AmbulanceRequestCreate, AmbulanceRequestCreateInternal,
    AmbulanceRequestRead,
    AmbulanceVehicleCreate,
    AmbulanceVehicleRead,
)


def _ref() -> str:
    return f"MH-AMB-{uuid.uuid4().hex[:8].upper()}"


class AmbulanceService:
    async def list_providers(self, db: AsyncSession, city: str | None = None, skip: int = 0, limit: int = 20) -> dict[str, Any]:
        filters: dict[str, Any] = {"is_active": True, "is_verified": True}
        if city:
            filters["city"] = city
        res = await crud_ambulance_providers.get_multi(
            db=db, offset=skip, limit=limit, schema_to_select=AmbulanceProviderRead, **filters
        )
        return dict(res)

    async def get_provider(self, provider_id: int, db: AsyncSession) -> dict[str, Any]:
        p = await crud_ambulance_providers.get(db=db, id=provider_id, is_active=True, schema_to_select=AmbulanceProviderRead)
        if not p:
            raise ResourceNotFoundError("Ambulance provider not found")
        return dict(p)

    async def create_provider(self, data: AmbulanceProviderCreate, db: AsyncSession) -> dict[str, Any]:
        if await crud_ambulance_providers.exists(db=db, registration_number=data.registration_number):
            raise ValidationError("Registration number already exists")
        created = await crud_ambulance_providers.create(db=db, object=data, schema_to_select=AmbulanceProviderRead)
        if not created:
            raise ValidationError("Failed to create provider")
        return dict(created)

    async def create_vehicle(self, data: AmbulanceVehicleCreate, db: AsyncSession) -> dict[str, Any]:
        await self.get_provider(data.provider_id, db)
        if await crud_ambulance_vehicles.exists(db=db, vehicle_number=data.vehicle_number):
            raise ValidationError("Vehicle number already registered")
        created = await crud_ambulance_vehicles.create(db=db, object=data, schema_to_select=AmbulanceVehicleRead)
        if not created:
            raise ValidationError("Failed to add vehicle")
        return dict(created)

    async def list_available_vehicles(self, db: AsyncSession, city: str | None = None) -> dict[str, Any]:
        res = await crud_ambulance_vehicles.get_multi(
            db=db, offset=0, limit=50, schema_to_select=AmbulanceVehicleRead, is_available=True
        )
        return dict(res)

    async def create_request(self, user_id: int, data: AmbulanceRequestCreate, db: AsyncSession) -> dict[str, Any]:
        req_data = {
            "request_ref": _ref(),
            "user_id": user_id,
            **data.model_dump(),
            "status": "pending",
        }

        created = await crud_ambulance_requests.create(db=db, object=AmbulanceRequestCreateInternal(**req_data), schema_to_select=AmbulanceRequestRead)
        if not created:
            raise ValidationError("Failed to create request")

        return dict(created)

    async def list_user_requests(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        res = await crud_ambulance_requests.get_multi(
            db=db, offset=0, limit=50, schema_to_select=AmbulanceRequestRead, user_id=user_id
        )
        return dict(res)

    async def get_request(self, req_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        r = await crud_ambulance_requests.get(db=db, id=req_id, user_id=user_id, schema_to_select=AmbulanceRequestRead)
        if not r:
            raise ResourceNotFoundError("Request not found")
        return dict(r)

    async def cancel_request(self, req_id: int, user_id: int, db: AsyncSession) -> None:
        r = await crud_ambulance_requests.get(db=db, id=req_id, user_id=user_id)
        if not r:
            raise ResourceNotFoundError("Request not found")
        if r["status"] not in ("pending", "assigned"):
            raise ValidationError("Only pending or assigned requests can be cancelled")

        await crud_ambulance_requests.update(db=db, object={"status": "cancelled"}, id=req_id)

        # If assigned, free up vehicle
        if r["vehicle_id"]:
            await crud_ambulance_vehicles.update(db=db, object={"is_available": True}, id=r["vehicle_id"])
