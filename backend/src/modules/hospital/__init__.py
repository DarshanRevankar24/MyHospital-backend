"""Hospital service module."""

from .models import HospitalBooking, HospitalDoctor, HospitalProvider, HospitalSlot

__all__ = ["HospitalProvider", "HospitalDoctor", "HospitalSlot", "HospitalBooking"]
