"""Ambulance Pydantic schemas."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .enums import AmbulanceRequestStatus, AmbulanceType


class AmbulanceProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    registration_number: str
    city: str
    state: str
    phone: str
    is_verified: bool


class AmbulanceProviderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[str, Field(min_length=2, max_length=120)]
    registration_number: Annotated[str, Field(min_length=2, max_length=60)]
    city: Annotated[str, Field(min_length=2, max_length=60)]
    state: Annotated[str, Field(min_length=2, max_length=60)]
    phone: Annotated[str, Field(min_length=10, max_length=15)]


class AmbulanceVehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider_id: int
    vehicle_number: str
    ambulance_type: str
    is_ac: bool
    is_available: bool


class AmbulanceVehicleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int
    vehicle_number: Annotated[str, Field(min_length=2, max_length=30)]
    ambulance_type: AmbulanceType
    is_ac: bool = True


class AmbulanceRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pickup_address: Annotated[str, Field(min_length=5, max_length=300)]
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None
    destination_address: Annotated[str, Field(min_length=5, max_length=300)]
    patient_name: Annotated[str, Field(min_length=2, max_length=80)]
    patient_condition: str | None = None
    ambulance_type: AmbulanceType = AmbulanceType.BASIC


class AmbulanceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    request_ref: str
    user_id: int
    provider_id: int | None = None
    vehicle_id: int | None = None
    pickup_address: str
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None
    destination_address: str
    patient_name: str
    patient_condition: str | None = None
    ambulance_type: str
    status: AmbulanceRequestStatus
    assigned_at: str | None = None
    estimated_arrival_min: int | None = None
