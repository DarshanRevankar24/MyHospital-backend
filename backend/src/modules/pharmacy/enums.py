from enum import StrEnum

class MedicineForm(StrEnum):
    TABLET = "tablet"; SYRUP = "syrup"; INJECTION = "injection"
    CREAM = "cream"; DROPS = "drops"; CAPSULE = "capsule"; OTHER = "other"

class DeliveryType(StrEnum):
    PICKUP = "pickup"; DELIVERY = "delivery"

class OrderStatus(StrEnum):
    PENDING = "pending"; CONFIRMED = "confirmed"; DISPENSED = "dispensed"
    DELIVERED = "delivered"; CANCELLED = "cancelled"
