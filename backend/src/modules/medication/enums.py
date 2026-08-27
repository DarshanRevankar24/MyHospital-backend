import enum


class MedicineType(str, enum.Enum):
    TABLET = "Tablet"
    SYRUP = "Syrup"
    INJECTION = "Injection"
    CAPSULE = "Capsule"
    DROPS = "Drops"
    OINTMENT = "Ointment"
    CREAM = "Cream"
    GEL = "Gel"
    POWDER = "Powder"
    OTHER = "Other"
