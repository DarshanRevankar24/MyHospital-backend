"""Initialize all modules and models to ensure SQLAlchemy registration."""

from .ambulance.models import AmbulanceProvider, AmbulanceRequest, AmbulanceVehicle
from .api_keys.models import APIKey, KeyPermission, KeyUsage
from .blood_bank.models import BloodBankProvider, BloodRequest, BloodStock
from .hospital.models import HospitalBooking, HospitalDoctor, HospitalProvider, HospitalSlot
from .laboratory.models import LabBooking, LabTest, LaboratoryProvider
from .pharmacy.models import Medicine, PharmacyOrder, PharmacyProvider
from .rate_limit.models import RateLimit
from .tier.models import Tier
from .user.models import User

__all__ = [
    "User",
    "Tier",
    "RateLimit",
    "APIKey",
    "KeyUsage",
    "KeyPermission",
    "HospitalProvider",
    "HospitalDoctor",
    "HospitalSlot",
    "HospitalBooking",
    "LaboratoryProvider",
    "LabTest",
    "LabBooking",
    "BloodBankProvider",
    "BloodStock",
    "BloodRequest",
    "PharmacyProvider",
    "Medicine",
    "PharmacyOrder",
    "AmbulanceProvider",
    "AmbulanceVehicle",
    "AmbulanceRequest",
]
