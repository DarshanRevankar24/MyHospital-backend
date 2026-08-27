"""Pharmacy Pydantic schemas."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .enums import DeliveryType, MedicineForm, OrderStatus


class PharmacyProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    license_number: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    pincode: str
    phone: str
    email: str | None = None
    is_delivery_available: bool
    delivery_radius_km: float
    is_24x7: bool
    is_verified: bool


class PharmacyProviderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, Field(min_length=2, max_length=120)]
    license_number: Annotated[str, Field(min_length=2, max_length=60)]
    address_line1: Annotated[str, Field(min_length=2, max_length=120)]
    address_line2: str | None = None
    city: Annotated[str, Field(min_length=2, max_length=60)]
    state: Annotated[str, Field(min_length=2, max_length=60)]
    pincode: Annotated[str, Field(pattern=r"^\d{6}$")]
    phone: Annotated[str, Field(min_length=10, max_length=15)]
    email: str | None = None
    is_delivery_available: bool = False
    delivery_radius_km: Annotated[float, Field(ge=0.0, default=5.0)]
    is_24x7: bool = False


class MedicineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider_id: int
    name: str
    brand: str | None = None
    generic_name: str | None = None
    category: str
    form: str
    strength: str | None = None
    price: Decimal
    stock_quantity: int
    requires_prescription: bool
    is_available: bool


class MedicineCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int
    name: Annotated[str, Field(min_length=2, max_length=120)]
    brand: str | None = None
    generic_name: str | None = None
    category: Annotated[str, Field(min_length=2, max_length=60)]
    form: MedicineForm
    strength: str | None = None
    price: Annotated[Decimal, Field(gt=0)]
    stock_quantity: Annotated[int, Field(ge=0, default=0)]
    requires_prescription: bool = False


class OrderItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    medicine_id: int
    quantity: Annotated[int, Field(ge=1)]


class PharmacyOrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int
    items: Annotated[list[OrderItemCreate], Field(min_length=1)]
    delivery_type: DeliveryType = DeliveryType.PICKUP
    delivery_address: str | None = None
    prescription_url: str | None = None
    patient_name: Annotated[str, Field(min_length=2, max_length=80)]
    patient_phone: Annotated[str, Field(min_length=10, max_length=15)]


class PharmacyOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_ref: str
    user_id: int
    provider_id: int
    items: list[dict]
    delivery_type: str
    delivery_address: str | None = None
    prescription_url: str | None = None
    patient_name: str
    patient_phone: str
    status: OrderStatus
    amount: Decimal


class PharmacyOrderCreateInternal(PharmacyOrderCreate):
    user_id: int
    order_ref: str
    status: str
    total_amount: float
