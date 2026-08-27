"""Blood Bank Pydantic schemas."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .enums import BloodGroup, BloodRequestStatus, Urgency


class BloodBankProviderRead(BaseModel):
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
    is_24x7: bool
    is_verified: bool


class BloodBankProviderCreate(BaseModel):
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
    is_24x7: bool = False


class BloodStockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider_id: int
    blood_group: str
    units_available: int


class BloodStockCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int
    blood_group: BloodGroup
    units_available: Annotated[int, Field(ge=0)]


class BloodRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int
    blood_group: BloodGroup
    units_required: Annotated[int, Field(ge=1, le=20)]
    urgency: Urgency = Urgency.NORMAL
    patient_name: Annotated[str, Field(min_length=2, max_length=80)]
    patient_hospital: str | None = None
    patient_contact: Annotated[str, Field(min_length=10, max_length=15)]
    required_by_date: str | None = None
    notes: str | None = None


class BloodRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    request_ref: str
    user_id: int
    provider_id: int
    blood_group: str
    units_required: int
    urgency: str
    patient_name: str
    patient_hospital: str | None = None
    patient_contact: str
    required_by_date: str | None = None
    status: BloodRequestStatus
    notes: str | None = None


class BloodRequestCreateInternal(BloodRequestCreate):
    user_id: int
    request_ref: str
    status: str
