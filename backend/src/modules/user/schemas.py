from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..common.schemas import PersistentDeletion, TimestampSchema
from .enums import BloodGroupEnum, GenderEnum, KYCDocumentType


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mask_doc_number(value: str) -> str:
    """Return a masked document number exposing only the last 4 characters."""
    if len(value) <= 4:
        return value
    return "*" * (len(value) - 4) + value[-4:]


# ── Base ──────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[
        str,
        Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"]),
    ]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]

    # ── Health profile ────────────────────────────────────────────────────────
    date_of_birth: Annotated[date, Field(examples=["1990-01-15"])]
    gender: Annotated[GenderEnum, Field(examples=["male"])]
    blood_group: Annotated[BloodGroupEnum, Field(examples=["O+"])]

    # ── KYC / Identity ────────────────────────────────────────────────────────
    kyc_document_type: Annotated[KYCDocumentType, Field(examples=["aadhaar"])]
    kyc_document_number: Annotated[
        str,
        Field(min_length=4, max_length=50, examples=["1234-5678-9012"]),
    ]

    # ── Address ───────────────────────────────────────────────────────────────
    address_line1: Annotated[str, Field(min_length=2, max_length=120, examples=["Flat 4B, Rose Apartments"])]
    address_line2: Annotated[str | None, Field(max_length=120, default=None, examples=["MG Road"])]
    city: Annotated[str, Field(min_length=2, max_length=60, examples=["Bengaluru"])]
    state: Annotated[str, Field(min_length=2, max_length=60, examples=["Karnataka"])]
    pincode: Annotated[
        str,
        Field(min_length=6, max_length=10, pattern=r"^\d{6}$", examples=["560001"]),
    ]
    country: Annotated[str, Field(min_length=2, max_length=60, default="India", examples=["India"])]

    # ── Contact ───────────────────────────────────────────────────────────────
    phone_number: Annotated[
        str,
        Field(
            min_length=10,
            max_length=15,
            pattern=r"^\+?[1-9]\d{9,14}$",
            examples=["+919876543210"],
            description="Phone number in E.164 format (e.g. +919876543210)",
        ),
    ]


# ── Full internal schema ──────────────────────────────────────────────────────

class User(TimestampSchema, UserBase, PersistentDeletion):
    """Complete user model with all fields."""

    hashed_password: str
    is_superuser: bool = False
    profile_image_url: Annotated[
        str,
        Field(
            default="https://www.profileimageurl.com",
            description="URL of the user's profile image",
        ),
    ]
    tier_id: int | None = None

    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None

    # Optional profile fields
    height_cm: float | None = None
    weight_kg: float | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


# ── Read (public) ─────────────────────────────────────────────────────────────

class UserRead(BaseModel):
    """Schema for reading user data, excludes sensitive information.

    The KYC document number is masked — only the last 4 characters are visible.
    """

    id: int
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[
        str,
        Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"]),
    ]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    profile_image_url: str
    is_deleted: bool = False
    tier_id: int | None
    is_superuser: bool = False
    email_verified: bool = False
    oauth_provider: str | None = None

    # Health profile
    date_of_birth: date
    gender: str
    blood_group: str
    height_cm: float | None = None
    weight_kg: float | None = None

    # KYC — masked
    kyc_document_type: str
    kyc_document_number: str  # will be masked by validator below

    # Address
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    pincode: str
    country: str

    # Contact
    phone_number: str
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    @field_validator("kyc_document_number", mode="before")
    @classmethod
    def mask_kyc(cls, v: str) -> str:
        return _mask_doc_number(v)


# ── Create ────────────────────────────────────────────────────────────────────

class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: Annotated[
        str,
        Field(
            min_length=8,
            description=(
                "Password must be at least 8 characters long and include a number,"
                "uppercase letter, lowercase letter, and special character"
            ),
            examples=["Str1ngst!"],
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
        ),
    ]
    # Optional at signup — can be filled via profile update later
    height_cm: float | None = None
    weight_kg: float | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


# ── Create Internal ───────────────────────────────────────────────────────────

class UserCreateInternal(UserBase):
    """Internal schema for user creation with hashed password."""

    hashed_password: str
    height_cm: float | None = None
    weight_kg: float | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None


# ── Update ────────────────────────────────────────────────────────────────────

class UserUpdate(BaseModel):
    """Schema for updating user data — all fields are optional."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str | None,
        Field(min_length=2, max_length=30, examples=["User Userberg"], default=None),
    ]
    username: Annotated[
        str | None,
        Field(
            min_length=2,
            max_length=20,
            pattern=r"^[a-z0-9]+$",
            examples=["userberg"],
            default=None,
        ),
    ]
    email: Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            examples=["https://www.profileimageurl.com"],
            default=None,
        ),
    ]

    # Health profile
    date_of_birth: date | None = None
    gender: GenderEnum | None = None
    blood_group: BloodGroupEnum | None = None
    height_cm: float | None = None
    weight_kg: float | None = None

    # KYC
    kyc_document_type: KYCDocumentType | None = None
    kyc_document_number: Annotated[str | None, Field(min_length=4, max_length=50, default=None)]

    # Address
    address_line1: Annotated[str | None, Field(min_length=2, max_length=120, default=None)]
    address_line2: Annotated[str | None, Field(max_length=120, default=None)]
    city: Annotated[str | None, Field(min_length=2, max_length=60, default=None)]
    state: Annotated[str | None, Field(min_length=2, max_length=60, default=None)]
    pincode: Annotated[str | None, Field(min_length=6, max_length=10, pattern=r"^\d{6}$", default=None)]
    country: Annotated[str | None, Field(min_length=2, max_length=60, default=None)]

    # Contact
    phone_number: Annotated[
        str | None,
        Field(min_length=10, max_length=15, pattern=r"^\+?[1-9]\d{9,14}$", default=None),
    ]
    emergency_contact_name: Annotated[str | None, Field(max_length=60, default=None)]
    emergency_contact_phone: Annotated[
        str | None,
        Field(max_length=15, pattern=r"^\+?[1-9]\d{9,14}$", default=None),
    ]

    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool | None = None
    oauth_updated_at: datetime | None = None


# ── Update Internal ───────────────────────────────────────────────────────────

class UserUpdateInternal(UserUpdate):
    """Internal schema for user updates."""

    updated_at: datetime


# ── Tier Update ───────────────────────────────────────────────────────────────

class UserTierUpdate(BaseModel):
    """Schema for updating a user's tier."""

    tier_id: int


# ── Soft Delete ───────────────────────────────────────────────────────────────

class UserDelete(BaseModel):
    """Schema for soft-deleting a user."""

    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


# ── GDPR Anonymize ────────────────────────────────────────────────────────────

class UserAnonymize(BaseModel):
    """Schema for GDPR/LGPD compliant user anonymization.

    This schema includes all fields that need to be updated during
    the user anonymization process for privacy compliance.
    """

    model_config = ConfigDict(extra="forbid")

    # Core identity — anonymized
    name: str
    username: str
    hashed_password: str | None = None
    profile_image_url: str | None = None
    tier_id: int | None = None
    is_superuser: bool = False
    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
    email_verified: bool = False
    oauth_created_at: datetime | None = None
    oauth_updated_at: datetime | None = None

    # Health profile — cleared
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None

    # KYC — cleared
    kyc_document_type: str | None = None
    kyc_document_number: str | None = None

    # Address — cleared
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str | None = None

    # Contact — cleared
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


# ── Restore Deleted ───────────────────────────────────────────────────────────

class UserRestoreDeleted(BaseModel):
    """Schema for restoring a deleted user."""

    is_deleted: bool
