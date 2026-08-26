from typing import Any

from pydantic import BaseModel, Field

from ..user.schemas import UserRead


class FamilyRequestCreate(BaseModel):
    identifier: str = Field(..., description="Phone number or username of the family member to connect with.")


class FamilyRequestUpdate(BaseModel):
    permissions: dict[str, Any] | None = Field(default=None, description="Optional permissions update")


class FamilyConnectionRead(BaseModel):
    id: int
    requester_id: int
    recipient_id: int
    status: str
    permissions: dict[str, Any] | None

    requester: UserRead | None = None
    recipient: UserRead | None = None

    class Config:
        from_attributes = True
