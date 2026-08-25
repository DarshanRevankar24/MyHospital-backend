from typing import Annotated
from fastapi import Depends
from .service import FamilyService

def get_family_service() -> FamilyService:
    """Get family service instance."""
    return FamilyService()

FamilyServiceDep = Annotated[FamilyService, Depends(get_family_service)]
