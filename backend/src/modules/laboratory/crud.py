from fastcrud import FastCRUD

from .models import LabBooking, LaboratoryProvider, LabTest

crud_lab_providers: FastCRUD = FastCRUD(LaboratoryProvider)
crud_lab_tests: FastCRUD = FastCRUD(LabTest)
crud_lab_bookings: FastCRUD = FastCRUD(LabBooking)
