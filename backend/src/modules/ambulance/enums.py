import enum


class AmbulanceType(str, enum.Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    NEONATAL = "neonatal"
    MORTUARY = "mortuary"


class AmbulanceRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
