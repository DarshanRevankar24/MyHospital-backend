"""Laboratory service module enums."""

from enum import StrEnum


class CollectionType(StrEnum):
    WALK_IN = "walk_in"
    HOME_COLLECTION = "home_collection"


class LabBookingStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SAMPLE_COLLECTED = "sample_collected"
    REPORT_READY = "report_ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestCategory(StrEnum):
    HAEMATOLOGY = "haematology"
    BIOCHEMISTRY = "biochemistry"
    MICROBIOLOGY = "microbiology"
    IMMUNOLOGY = "immunology"
    PATHOLOGY = "pathology"
    RADIOLOGY = "radiology"
    CARDIOLOGY = "cardiology"
    URINE = "urine"
    HORMONE = "hormone"
    VITAMIN = "vitamin"
    ALLERGY = "allergy"
    OTHER = "other"
