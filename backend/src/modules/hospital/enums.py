"""Hospital service module enums."""

from enum import StrEnum


class BookingStatus(StrEnum):
    """Universal booking status for all service modules."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Speciality(StrEnum):
    """Hospital medical specialities."""

    GENERAL = "general_medicine"
    CARDIOLOGY = "cardiology"
    ORTHOPAEDICS = "orthopaedics"
    NEUROLOGY = "neurology"
    GYNAECOLOGY = "gynaecology"
    PAEDIATRICS = "paediatrics"
    DERMATOLOGY = "dermatology"
    OPHTHALMOLOGY = "ophthalmology"
    ENT = "ent"
    PSYCHIATRY = "psychiatry"
    ONCOLOGY = "oncology"
    UROLOGY = "urology"
    NEPHROLOGY = "nephrology"
    GASTROENTEROLOGY = "gastroenterology"
    PULMONOLOGY = "pulmonology"
    ENDOCRINOLOGY = "endocrinology"
    RADIOLOGY = "radiology"
    DENTISTRY = "dentistry"
    PHYSIOTHERAPY = "physiotherapy"
    EMERGENCY = "emergency"
