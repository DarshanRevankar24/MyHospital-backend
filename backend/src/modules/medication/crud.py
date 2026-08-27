from fastcrud import FastCRUD

from .models import Medication

crud_medications: FastCRUD = FastCRUD(Medication, is_deleted_column="is_deleted", deleted_at_column="deleted_at")
