from typing import Any

from fastapi import APIRouter

from ...infrastructure.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import MedicationServiceDep
from .schemas import MedicationCreate, MedicationUpdate

router = APIRouter(tags=["Medication Tracking"])


@router.get("/", summary="Get own medications")
async def get_medications(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: MedicationServiceDep,
) -> list[dict[str, Any]]:
    """List all your medications and pill reminders."""
    return await service.get_user_medications(user_id=current_user["id"], db=db)


@router.post("/", summary="Add a medication", status_code=201)
async def add_medication(
    data: MedicationCreate,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: MedicationServiceDep,
) -> dict[str, Any]:
    """Add a new medicine to your schedule."""
    return await service.create_medication(
        user_id=current_user["id"], creator_id=current_user["id"], data=data, db=db
    )


@router.patch("/{medication_id}", summary="Update a medication")
async def update_medication(
    medication_id: int,
    data: MedicationUpdate,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: MedicationServiceDep,
) -> dict[str, Any]:
    """Update dosage, timings, or instructions for a medicine."""
    return await service.update_medication(
        medication_id=medication_id, user_id=current_user["id"], data=data, db=db
    )


@router.delete("/{medication_id}", summary="Delete a medication")
async def delete_medication(
    medication_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: MedicationServiceDep,
) -> dict[str, str]:
    """Remove a medicine from your schedule."""
    await service.delete_medication(medication_id=medication_id, user_id=current_user["id"], db=db)
    return {"message": "Medication deleted successfully"}
