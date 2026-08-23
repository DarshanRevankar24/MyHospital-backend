"""User enums for OAuth provider management and health/identity profile."""

from enum import StrEnum


class OAuthProvider(StrEnum):
    """OAuth provider types for user authentication.

    These values are used to identify the OAuth provider used for registration
    and login. The string values must match the provider names used in the
    OAuth configuration and factory registration.
    """

    GOOGLE = "google"
    GITHUB = "github"


class GenderEnum(StrEnum):
    """Biological / self-identified gender options."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroupEnum(StrEnum):
    """ABO + Rh blood group system."""

    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class KYCDocumentType(StrEnum):
    """Accepted government-issued identity document types for KYC verification."""

    AADHAAR = "aadhaar"
    PAN = "pan"
    PASSPORT = "passport"
    DRIVING_LICENCE = "driving_licence"
    VOTER_ID = "voter_id"
