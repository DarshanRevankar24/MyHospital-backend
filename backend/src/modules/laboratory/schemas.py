"""Laboratory module Pydantic schemas."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .enums import CollectionType, LabBookingStatus, TestCategory


class LaboratoryProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    registration_number: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    pincode: str
    phone: str
    email: str | None = None
    is_home_collection_available: bool
    home_collection_charge: Decimal
    is_verified: bool
    logo_url: str | None = None


class LaboratoryProviderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, Field(min_length=2, max_length=120)]
    registration_number: Annotated[str, Field(min_length=2, max_length=60)]
    address_line1: Annotated[str, Field(min_length=2, max_length=120)]
    address_line2: str | None = None
    city: Annotated[str, Field(min_length=2, max_length=60)]
    state: Annotated[str, Field(min_length=2, max_length=60)]
    pincode: Annotated[str, Field(pattern=r"^\d{6}$")]
    phone: Annotated[str, Field(min_length=10, max_length=15)]
    email: str | None = None
    is_home_collection_available: bool = False
    home_collection_charge: Decimal = Decimal("0")
    logo_url: str | None = None


class LabTestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider_id: int
    test_name: str
    test_code: str
    description: str | None = None
    category: str
    price: Decimal
    discount_price: Decimal | None = None
    preparation_instructions: str | None = None
    report_in_hours: int
    is_available: bool


class LabTestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int
    test_name: Annotated[str, Field(min_length=2, max_length=120)]
    test_code: Annotated[str, Field(min_length=1, max_length=30)]
    description: str | None = None
    category: TestCategory
    price: Annotated[Decimal, Field(gt=0)]
    discount_price: Decimal | None = None
    preparation_instructions: str | None = None
    report_in_hours: Annotated[int, Field(ge=1, le=720, default=24)]


class LabBookingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int
    test_ids: Annotated[list[int], Field(min_length=1)]
    collection_type: CollectionType = CollectionType.WALK_IN
    collection_date: str | None = None
    collection_time_slot: str | None = None
    collection_address: str | None = None
    patient_name: Annotated[str, Field(min_length=2, max_length=80)]
    patient_phone: Annotated[str, Field(min_length=10, max_length=15)]


class LabBookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    booking_ref: str
    user_id: int
    provider_id: int
    test_ids: list[int]
    collection_type: str
    collection_date: str | None = None
    collection_time_slot: str | None = None
    collection_address: str | None = None
    patient_name: str
    patient_phone: str
    status: LabBookingStatus
    amount: Decimal
    report_url: str | None = None


class LabBookingCreateInternal(LabBookingCreate):
    user_id: int
    booking_ref: str
    status: str
    amount: float
