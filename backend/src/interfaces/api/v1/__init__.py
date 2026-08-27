from fastapi import APIRouter

from ....infrastructure.auth.routes import router as auth_router
from ....modules.ambulance.routes import router as ambulance_router
from ....modules.api_keys.routes import router as api_keys_router
from ....modules.blood_bank.routes import router as blood_bank_router
from ....modules.family.routes import router as family_router
from ....modules.hospital.routes import router as hospital_router
from ....modules.laboratory.routes import router as laboratory_router
from ....modules.medication.routes import router as medication_router
from ....modules.notification.routes import router as notification_router
from ....modules.pharmacy.routes import router as pharmacy_router
from ....modules.rate_limit.routes import router as rate_limits_router
from ....modules.tier.routes import router as tiers_router
from ....modules.user.routes import router as users_router
from .metadata import router as metadata_router

router = APIRouter(prefix="/v1")
router.include_router(users_router, prefix="/users")
router.include_router(tiers_router, prefix="/tiers")
router.include_router(rate_limits_router, prefix="/rate-limits")
router.include_router(auth_router, prefix="/auth")
router.include_router(api_keys_router, prefix="/api-keys")
router.include_router(family_router, prefix="/family")
router.include_router(medication_router, prefix="/medications")
router.include_router(notification_router)
router.include_router(metadata_router, prefix="/metadata")

# Services
router.include_router(hospital_router, prefix="/services/hospital")
router.include_router(laboratory_router, prefix="/services/laboratory")
router.include_router(blood_bank_router, prefix="/services/blood-bank")
router.include_router(pharmacy_router, prefix="/services/pharmacy")
router.include_router(ambulance_router, prefix="/services/ambulance")
