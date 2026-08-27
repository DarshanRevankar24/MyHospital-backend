from fastcrud import FastCRUD

from .models import FamilyConnection

crud_family_connection: FastCRUD = FastCRUD(FamilyConnection, is_deleted_column="is_deleted", deleted_at_column="deleted_at")
