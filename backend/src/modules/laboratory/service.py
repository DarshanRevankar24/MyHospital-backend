"""Laboratory service layer."""

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceNotFoundError, ValidationError
from .crud import crud_lab_bookings, crud_lab_providers, crud_lab_tests
from .schemas import (
    LabBookingCreate,
    LabBookingRead,
    LaboratoryProviderCreate,
    LaboratoryProviderRead,
    LabTestCreate,
    LabTestRead,
)


def _ref() -> str:
    return f"MH-LAB-{uuid.uuid4().hex[:8].upper()}"


class LaboratoryService:
    async def list_providers(
        self,
        db: AsyncSession,
        city: str | None = None,
        home_collection: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> dict[str, Any]:
        filters: dict[str, Any] = {"is_active": True, "is_verified": True}
        if city:
            filters["city"] = city
        if home_collection is not None:
            filters["is_home_collection_available"] = home_collection
        res = await crud_lab_providers.get_multi(
            db=db, offset=skip, limit=limit, schema_to_select=LaboratoryProviderRead, **filters
        )
        return dict(res)

    async def get_provider(self, provider_id: int, db: AsyncSession) -> dict[str, Any]:
        p = await crud_lab_providers.get(db=db, id=provider_id, is_active=True, schema_to_select=LaboratoryProviderRead)
        if not p:
            raise ResourceNotFoundError("Laboratory not found")
        return dict(p)

    async def create_provider(self, data: LaboratoryProviderCreate, db: AsyncSession) -> dict[str, Any]:
        if await crud_lab_providers.exists(db=db, registration_number=data.registration_number):
            raise ValidationError("Registration number already exists")
        created = await crud_lab_providers.create(db=db, object=data.model_dump(), schema_to_select=LaboratoryProviderRead)
        if not created:
            raise ValidationError("Failed to create provider")
        return dict(created)

    async def list_tests(
        self, provider_id: int, db: AsyncSession, category: str | None = None, name: str | None = None
    ) -> dict[str, Any]:
        filters: dict[str, Any] = {"provider_id": provider_id, "is_available": True}
        if category:
            filters["category"] = category
        res = await crud_lab_tests.get_multi(db=db, offset=0, limit=200, schema_to_select=LabTestRead, **filters)
        return dict(res)

    async def search_tests(self, db: AsyncSession, name: str) -> dict[str, Any]:
        res = await crud_lab_tests.get_multi(db=db, offset=0, limit=50, schema_to_select=LabTestRead, is_available=True)
        return dict(res)

    async def create_test(self, data: LabTestCreate, db: AsyncSession) -> dict[str, Any]:
        await self.get_provider(data.provider_id, db)
        created = await crud_lab_tests.create(db=db, object=data.model_dump(), schema_to_select=LabTestRead)
        if not created:
            raise ValidationError("Failed to create test")
        return dict(created)

    async def create_booking(self, user_id: int, data: LabBookingCreate, db: AsyncSession) -> dict[str, Any]:
        provider = await crud_lab_providers.get(db=db, id=data.provider_id, is_active=True)
        if not provider:
            raise ResourceNotFoundError("Laboratory not found")

        # Calculate total from selected tests
        total = Decimal("0")
        for test_id in data.test_ids:
            test = await crud_lab_tests.get(db=db, id=test_id, is_available=True)
            if not test:
                raise ResourceNotFoundError(f"Test {test_id} not found or unavailable")
            total += test["discount_price"] or test["price"]

        if data.collection_type == "home_collection":
            total += provider["home_collection_charge"] or Decimal("0")

        booking_data = {
            "booking_ref": _ref(),
            "user_id": user_id,
            "provider_id": data.provider_id,
            "test_ids": data.test_ids,
            "collection_type": data.collection_type,
            "collection_date": data.collection_date,
            "collection_time_slot": data.collection_time_slot,
            "collection_address": data.collection_address,
            "patient_name": data.patient_name,
            "patient_phone": data.patient_phone,
            "status": "pending",
            "amount": total,
        }

        created = await crud_lab_bookings.create(db=db, object=booking_data, schema_to_select=LabBookingRead)
        if not created:
            raise ValidationError("Failed to create booking")
        return dict(created)

    async def list_user_bookings(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        res = await crud_lab_bookings.get_multi(db=db, offset=0, limit=50, schema_to_select=LabBookingRead, user_id=user_id)
        return dict(res)

    async def get_booking(self, booking_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        b = await crud_lab_bookings.get(db=db, id=booking_id, user_id=user_id, schema_to_select=LabBookingRead)
        if not b:
            raise ResourceNotFoundError("Booking not found")
        return dict(b)

    async def cancel_booking(self, booking_id: int, user_id: int, db: AsyncSession) -> None:
        b = await crud_lab_bookings.get(db=db, id=booking_id, user_id=user_id)
        if not b:
            raise ResourceNotFoundError("Booking not found")
        if b["status"] not in ("pending", "confirmed"):
            raise ValidationError("Cannot cancel this booking")
        await crud_lab_bookings.update(db=db, object={"status": "cancelled"}, id=booking_id)
