from typing import Annotated

from fastapi import Depends

from .service import BloodBankService


def get_blood_bank_service() -> BloodBankService:
    return BloodBankService()


BloodBankServiceDep = Annotated[BloodBankService, Depends(get_blood_bank_service)]
