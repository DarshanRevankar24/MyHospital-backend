from fastcrud import FastCRUD

from .models import Medication

crud_medications: FastCRUD = FastCRUD(Medication)
