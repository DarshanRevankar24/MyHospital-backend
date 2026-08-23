"""Hospital module FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends

from .service import HospitalService


def get_hospital_service() -> HospitalService:
    return HospitalService()


HospitalServiceDep = Annotated[HospitalService, Depends(get_hospital_service)]
