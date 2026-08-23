from typing import Annotated
from fastapi import Depends
from .service import AmbulanceService

def get_ambulance_service() -> AmbulanceService:
    return AmbulanceService()

AmbulanceServiceDep = Annotated[AmbulanceService, Depends(get_ambulance_service)]
