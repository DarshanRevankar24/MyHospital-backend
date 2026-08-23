from typing import Annotated
from fastapi import Depends
from .service import PharmacyService

def get_pharmacy_service() -> PharmacyService:
    return PharmacyService()

PharmacyServiceDep = Annotated[PharmacyService, Depends(get_pharmacy_service)]
