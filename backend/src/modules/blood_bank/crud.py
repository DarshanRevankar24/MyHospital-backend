from fastcrud import FastCRUD

from .models import BloodBankProvider, BloodRequest, BloodStock

crud_blood_bank_providers: FastCRUD = FastCRUD(BloodBankProvider)
crud_blood_stocks: FastCRUD = FastCRUD(BloodStock)
crud_blood_requests: FastCRUD = FastCRUD(BloodRequest)
