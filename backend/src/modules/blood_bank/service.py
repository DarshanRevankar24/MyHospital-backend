"""Blood Bank service layer."""

import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..common.exceptions import ResourceNotFoundError, ValidationError
from .crud import crud_blood_bank_providers, crud_blood_requests, crud_blood_stocks
from .schemas import (BloodBankProviderCreate, BloodBankProviderRead, BloodRequestCreate,
                      BloodRequestRead, BloodStockCreate, BloodStockRead)


def _ref() -> str:
    return f"MH-BB-{uuid.uuid4().hex[:8].upper()}"


class BloodBankService:

    async def list_providers(self, db: AsyncSession, city: str | None = None,
                              skip: int = 0, limit: int = 20) -> dict[str, Any]:
        filters: dict[str, Any] = {"is_active": True, "is_verified": True}
        if city: filters["city"] = city
        return await crud_blood_bank_providers.get_multi(db=db, offset=skip, limit=limit,
                                                          schema_to_select=BloodBankProviderRead, **filters)

    async def get_provider(self, provider_id: int, db: AsyncSession) -> dict[str, Any]:
        p = await crud_blood_bank_providers.get(db=db, id=provider_id, is_active=True,
                                                  schema_to_select=BloodBankProviderRead)
        if not p: raise ResourceNotFoundError("Blood bank not found")
        return p

    async def create_provider(self, data: BloodBankProviderCreate, db: AsyncSession) -> dict[str, Any]:
        if await crud_blood_bank_providers.exists(db=db, license_number=data.license_number):
            raise ValidationError("License number already registered")
        created = await crud_blood_bank_providers.create(db=db, object=data, schema_to_select=BloodBankProviderRead)
        if not created: raise ValidationError("Failed to create provider")
        return created

    async def get_stock(self, provider_id: int, db: AsyncSession) -> dict[str, Any]:
        await self.get_provider(provider_id, db)
        return await crud_blood_stocks.get_multi(db=db, offset=0, limit=20,
                                                  schema_to_select=BloodStockRead, provider_id=provider_id)

    async def search_blood_group(self, blood_group: str, db: AsyncSession) -> dict[str, Any]:
        return await crud_blood_stocks.get_multi(db=db, offset=0, limit=50,
                                                  schema_to_select=BloodStockRead, blood_group=blood_group)

    async def upsert_stock(self, data: BloodStockCreate, db: AsyncSession) -> dict[str, Any]:
        existing = await crud_blood_stocks.get(db=db, provider_id=data.provider_id, blood_group=data.blood_group)
        if existing:
            updated = await crud_blood_stocks.update(db=db, object={"units_available": data.units_available},
                                                      id=existing["id"])
            return updated or existing
        created = await crud_blood_stocks.create(db=db, object=data, schema_to_select=BloodStockRead)
        if not created: raise ValidationError("Failed to update stock")
        return created

    async def create_request(self, user_id: int, data: BloodRequestCreate, db: AsyncSession) -> dict[str, Any]:
        await self.get_provider(data.provider_id, db)
        stock = await crud_blood_stocks.get(db=db, provider_id=data.provider_id, blood_group=data.blood_group)
        if not stock or stock["units_available"] < data.units_required:
            raise ValidationError(f"Insufficient {data.blood_group} units at this blood bank")
        req_data = {"request_ref": _ref(), "user_id": user_id, **data.model_dump(), "status": "pending"}
        from fastcrud import FastCRUD
        from .models import BloodRequest
        created = await FastCRUD(BloodRequest).create(db=db, object=req_data, schema_to_select=BloodRequestRead)
        if not created: raise ValidationError("Failed to create request")
        return created

    async def list_user_requests(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        return await crud_blood_requests.get_multi(db=db, offset=0, limit=50,
                                                    schema_to_select=BloodRequestRead, user_id=user_id)

    async def get_request(self, req_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        r = await crud_blood_requests.get(db=db, id=req_id, user_id=user_id, schema_to_select=BloodRequestRead)
        if not r: raise ResourceNotFoundError("Request not found")
        return r

    async def cancel_request(self, req_id: int, user_id: int, db: AsyncSession) -> None:
        r = await crud_blood_requests.get(db=db, id=req_id, user_id=user_id)
        if not r: raise ResourceNotFoundError("Request not found")
        if r["status"] not in ("pending",): raise ValidationError("Only pending requests can be cancelled")
        await crud_blood_requests.update(db=db, object={"status": "cancelled"}, id=req_id)
