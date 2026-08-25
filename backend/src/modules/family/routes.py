from typing import Any
from fastapi import APIRouter

from ...infrastructure.dependencies import AsyncSessionDep, CurrentUserDep
from .schemas import FamilyRequestCreate, FamilyConnectionRead
from .dependencies import FamilyServiceDep

router = APIRouter(tags=["Family"])

@router.post("/request", summary="Send a family request")
async def send_family_request(
    request_data: FamilyRequestCreate,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Send a family connection request using username or phone number."""
    return await service.send_family_request(
        requester_id=current_user["id"], 
        request_data=request_data, 
        db=db
    )

@router.get("/requests", summary="Get pending requests")
async def get_requests(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Get pending family requests (both incoming and outgoing)."""
    return await service.get_requests(user_id=current_user["id"], db=db)

@router.post("/requests/{connection_id}/accept", summary="Accept family request")
async def accept_request(
    connection_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Accept a pending family request."""
    return await service.accept_request(
        connection_id=connection_id, 
        user_id=current_user["id"], 
        db=db
    )

@router.post("/requests/{connection_id}/reject", summary="Reject family request")
async def reject_request(
    connection_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Reject a pending family request."""
    return await service.reject_request(
        connection_id=connection_id, 
        user_id=current_user["id"], 
        db=db
    )

@router.get("/members", summary="Get family members")
async def get_family_members(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> list[dict[str, Any]]:
    """List all connected family members."""
    return await service.get_family_members(user_id=current_user["id"], db=db)

@router.delete("/members/{connection_id}", summary="Remove family member")
async def remove_family_member(
    connection_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, str]:
    """Remove a family connection."""
    await service.remove_member(
        connection_id=connection_id, 
        user_id=current_user["id"], 
        db=db
    )
    return {"message": "Family member removed successfully"}
