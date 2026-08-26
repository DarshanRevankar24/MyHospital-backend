from fastcrud import FastCRUD

from .models import Medicine, PharmacyOrder, PharmacyProvider

crud_pharmacy_providers: FastCRUD = FastCRUD(PharmacyProvider)
crud_medicines: FastCRUD = FastCRUD(Medicine)
crud_pharmacy_orders: FastCRUD = FastCRUD(PharmacyOrder)
