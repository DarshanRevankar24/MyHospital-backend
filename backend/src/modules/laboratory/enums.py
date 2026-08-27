"""Laboratory service module enums."""

import enum


class CollectionType(str, enum.Enum):
    WALK_IN = "walk_in"
    HOME_COLLECTION = "home_collection"


class LabBookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SAMPLE_COLLECTED = "sample_collected"
    REPORT_READY = "report_ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestCategory(str, enum.Enum):
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
