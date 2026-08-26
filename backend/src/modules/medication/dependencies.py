from typing import Annotated

from fastapi import Depends

from .service import MedicationService


def get_medication_service() -> MedicationService:
    """Dependency provider for MedicationService."""
    return MedicationService()


MedicationServiceDep = Annotated[MedicationService, Depends(get_medication_service)]
