from fastcrud import FastCRUD
from .models import LaboratoryProvider, LabTest, LabBooking

crud_lab_providers: FastCRUD = FastCRUD(LaboratoryProvider)
crud_lab_tests: FastCRUD = FastCRUD(LabTest)
crud_lab_bookings: FastCRUD = FastCRUD(LabBooking)
