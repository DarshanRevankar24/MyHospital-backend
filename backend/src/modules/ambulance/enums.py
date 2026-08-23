from enum import StrEnum

class AmbulanceType(StrEnum):
    BASIC = "basic"
    ADVANCED = "advanced"
    NEONATAL = "neonatal"
    MORTUARY = "mortuary"

class AmbulanceRequestStatus(StrEnum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
