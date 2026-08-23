"""Hospital module CRUD instances."""

from fastcrud import FastCRUD

from .models import HospitalBooking, HospitalDoctor, HospitalProvider, HospitalSlot

crud_hospital_providers: FastCRUD = FastCRUD(HospitalProvider)
crud_hospital_doctors: FastCRUD = FastCRUD(HospitalDoctor)
crud_hospital_slots: FastCRUD = FastCRUD(HospitalSlot)
crud_hospital_bookings: FastCRUD = FastCRUD(HospitalBooking)
