from typing import Annotated

from fastapi import Depends

from .service import LaboratoryService


def get_laboratory_service() -> LaboratoryService:
    return LaboratoryService()


LaboratoryServiceDep = Annotated[LaboratoryService, Depends(get_laboratory_service)]
