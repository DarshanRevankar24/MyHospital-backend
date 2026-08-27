"""Family Pydantic schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..user.schemas import UserRead
from .enums import RelationType


class FamilyRequestCreate(BaseModel):
    """Schema for sending a family connection request."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(..., description="Username or phone number of the family member to connect with.")
    relation: RelationType = Field(..., description="Your relationship to this person (e.g. spouse, parent, child).")
    message: str | None = Field(
        default=None,
        max_length=300,
        description="Optional personal note to include with the request.",
    )


class FamilyRequestUpdate(BaseModel):
    """Schema for updating family connection settings."""

    model_config = ConfigDict(extra="forbid")

    permissions: dict[str, Any] | None = Field(default=None, description="Optional permissions update.")
    document_access_enabled: bool | None = Field(
        default=None,
        description="Enable or disable mutual medical document access for this connection.",
    )


class FamilyConnectionRead(BaseModel):
    """Schema for reading a family connection."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_id: int
    recipient_id: int
    status: str
    relation: str
    document_access_enabled: bool
    permissions: dict[str, Any] | None
    message: str | None = None

    requester: UserRead | None = None
    recipient: UserRead | None = None


class FamilyConnectionCreateInternal(FamilyConnectionCreate):
    requester_id: int
    recipient_id: int
    status: str
    permissions: dict
    document_access_enabled: bool
