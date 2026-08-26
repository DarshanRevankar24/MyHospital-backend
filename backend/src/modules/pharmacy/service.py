"""Pharmacy service layer."""

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceNotFoundError, ValidationError
from .crud import crud_medicines, crud_pharmacy_orders, crud_pharmacy_providers
from .schemas import (
    MedicineCreate,
    MedicineRead,
    PharmacyOrderCreate,
    PharmacyOrderRead,
    PharmacyProviderCreate,
    PharmacyProviderRead,
)


def _ref() -> str:
    return f"MH-PHRM-{uuid.uuid4().hex[:8].upper()}"


class PharmacyService:
    async def list_providers(
        self,
        db: AsyncSession,
        city: str | None = None,
        delivery: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> dict[str, Any]:
        filters: dict[str, Any] = {"is_active": True, "is_verified": True}
        if city:
            filters["city"] = city
        if delivery is not None:
            filters["is_delivery_available"] = delivery
        res = await crud_pharmacy_providers.get_multi(
            db=db, offset=skip, limit=limit, schema_to_select=PharmacyProviderRead, **filters
        )
        return dict(res)

    async def get_provider(self, provider_id: int, db: AsyncSession) -> dict[str, Any]:
        p = await crud_pharmacy_providers.get(db=db, id=provider_id, is_active=True, schema_to_select=PharmacyProviderRead)
        if not p:
            raise ResourceNotFoundError("Pharmacy not found")
        return dict(p)

    async def create_provider(self, data: PharmacyProviderCreate, db: AsyncSession) -> dict[str, Any]:
        if await crud_pharmacy_providers.exists(db=db, license_number=data.license_number):
            raise ValidationError("License number already registered")
        created = await crud_pharmacy_providers.create(db=db, object=data.model_dump(), schema_to_select=PharmacyProviderRead)
        if not created:
            raise ValidationError("Failed to create pharmacy")
        return dict(created)

    async def list_medicines(
        self, provider_id: int, db: AsyncSession, category: str | None = None, name: str | None = None
    ) -> dict[str, Any]:
        filters: dict[str, Any] = {"provider_id": provider_id, "is_available": True}
        if category:
            filters["category"] = category
        res = await crud_medicines.get_multi(db=db, offset=0, limit=200, schema_to_select=MedicineRead, **filters)
        return dict(res)

    async def search_medicines(self, db: AsyncSession, name: str) -> dict[str, Any]:
        res = await crud_medicines.get_multi(db=db, offset=0, limit=50, schema_to_select=MedicineRead, is_available=True, name=name)
        return dict(res)

    async def create_medicine(self, data: MedicineCreate, db: AsyncSession) -> dict[str, Any]:
        await self.get_provider(data.provider_id, db)
        created = await crud_medicines.create(db=db, object=data.model_dump(), schema_to_select=MedicineRead)
        if not created:
            raise ValidationError("Failed to add medicine")
        return dict(created)

    async def create_order(self, user_id: int, data: PharmacyOrderCreate, db: AsyncSession) -> dict[str, Any]:
        provider = await crud_pharmacy_providers.get(db=db, id=data.provider_id, is_active=True)
        if not provider:
            raise ResourceNotFoundError("Pharmacy not found")

        total = Decimal("0")
        order_items = []
        requires_rx = False

        for item_data in data.items:
            med = await crud_medicines.get(db=db, id=item_data.medicine_id, is_available=True)
            if not med or med["provider_id"] != data.provider_id:
                raise ResourceNotFoundError(f"Medicine {item_data.medicine_id} not available here")
            if med["stock_quantity"] < item_data.quantity:
                raise ValidationError(f"Insufficient stock for {med['name']}")

            if med["requires_prescription"]:
                requires_rx = True

            total += med["price"] * item_data.quantity
            order_items.append(
                {
                    "medicine_id": med["id"],
                    "name": med["name"],
                    "quantity": item_data.quantity,
                    "unit_price": str(med["price"]),
                    "subtotal": str(med["price"] * item_data.quantity),
                }
            )

        if requires_rx and not data.prescription_url:
            raise ValidationError("A prescription is required for one or more medicines in this order")

        if data.delivery_type == "delivery":
            if not provider["is_delivery_available"]:
                raise ValidationError("This pharmacy does not offer delivery")
            if not data.delivery_address:
                raise ValidationError("Delivery address required for delivery orders")

        order_data = {
            "order_ref": _ref(),
            "user_id": user_id,
            "provider_id": data.provider_id,
            "items": order_items,
            "delivery_type": data.delivery_type,
            "delivery_address": data.delivery_address,
            "prescription_url": data.prescription_url,
            "patient_name": data.patient_name,
            "patient_phone": data.patient_phone,
            "status": "pending",
            "amount": total,
        }

        # Deduct stock
        for item in data.items:
            med = await crud_medicines.get(db=db, id=item.medicine_id)
            if med:
                await crud_medicines.update(
                    db=db, object={"stock_quantity": med["stock_quantity"] - item.quantity}, id=med["id"]
                )

        created = await crud_pharmacy_orders.create(db=db, object=order_data, schema_to_select=PharmacyOrderRead)
        if not created:
            raise ValidationError("Failed to place order")
        return dict(created)

    async def list_user_orders(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        res = await crud_pharmacy_orders.get_multi(
            db=db, offset=0, limit=50, schema_to_select=PharmacyOrderRead, user_id=user_id
        )
        return dict(res)

    async def get_order(self, order_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        o = await crud_pharmacy_orders.get(db=db, id=order_id, user_id=user_id, schema_to_select=PharmacyOrderRead)
        if not o:
            raise ResourceNotFoundError("Order not found")
        return dict(o)

    async def cancel_order(self, order_id: int, user_id: int, db: AsyncSession) -> None:
        o = await crud_pharmacy_orders.get(db=db, id=order_id, user_id=user_id)
        if not o:
            raise ResourceNotFoundError("Order not found")
        if o["status"] not in ("pending",):
            raise ValidationError("Only pending orders can be cancelled")
        await crud_pharmacy_orders.update(db=db, object={"status": "cancelled"}, id=order_id)

        # Restore stock
        for item in o["items"]:
            med = await crud_medicines.get(db=db, id=item["medicine_id"])
            if med:
                await crud_medicines.update(
                    db=db, object={"stock_quantity": med["stock_quantity"] + item["quantity"]}, id=med["id"]
                )
