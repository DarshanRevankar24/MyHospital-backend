from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import crud_medications
from .schemas import MedicationCreate, MedicationRead, MedicationUpdate


class MedicationService:
    """Service for managing user medications and pill reminders."""

    async def get_user_medications(self, user_id: int, db: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Get all medications for a user."""
        res = await crud_medications.get_multi(
            db=db, 
            user_id=user_id, 
            is_deleted=False, 
            schema_to_select=MedicationRead,
            limit=limit,
            offset=offset
        )
        return res.get("data", []) if isinstance(res, dict) else []

    async def create_medication(
        self, user_id: int, creator_id: int, data: MedicationCreate, db: AsyncSession
    ) -> dict[str, Any]:
        """Create a new medication entry."""
        create_data = data.model_dump()
        create_data["user_id"] = user_id
        create_data["created_by_user_id"] = creator_id
        
        created = await crud_medications.create(
            db=db, object=create_data, schema_to_select=MedicationRead
        )
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create medication.")
        return created

    async def update_medication(
        self, medication_id: int, user_id: int, data: MedicationUpdate, db: AsyncSession
    ) -> dict[str, Any]:
        """Update an existing medication entry."""
        med = await crud_medications.get(db=db, id=medication_id, is_deleted=False)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found.")
            
        if med["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this medication.")
            
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update.")
            
        updated = await crud_medications.update(
            db=db, id=medication_id, object=update_data, schema_to_select=MedicationRead
        )
        return updated

    async def delete_medication(self, medication_id: int, user_id: int, db: AsyncSession) -> None:
        """Delete a medication entry."""
        med = await crud_medications.get(db=db, id=medication_id, is_deleted=False)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found.")
            
        if med["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this medication.")
            
        await crud_medications.delete(db=db, id=medication_id)
