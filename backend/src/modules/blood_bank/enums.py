from enum import StrEnum


class BloodGroup(StrEnum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class Urgency(StrEnum):
    NORMAL = "normal"
    URGENT = "urgent"
    CRITICAL = "critical"


class BloodRequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    FULFILLED = "fulfilled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
