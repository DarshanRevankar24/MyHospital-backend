import enum


class MedicineForm(str, enum.Enum):
    TABLET = "tablet"
    SYRUP = "syrup"
    INJECTION = "injection"
    CREAM = "cream"
    DROPS = "drops"
    CAPSULE = "capsule"
    OTHER = "other"


class DeliveryType(str, enum.Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISPENSED = "dispensed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
