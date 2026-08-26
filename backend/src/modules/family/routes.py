"""Family API routes."""

from typing import Any

from fastapi import APIRouter

from ...infrastructure.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import FamilyServiceDep
from .schemas import FamilyRequestCreate, FamilyRequestUpdate

router = APIRouter(tags=["Family"])


@router.post("/request", summary="Send a family connection request", status_code=201)
async def send_family_request(
    request_data: FamilyRequestCreate,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Send a family connection request using username or phone number.

    You must declare your relationship to the person (e.g. spouse, parent, child).
    An optional personal message can also be included.
    A push + SMS notification will be sent to the recipient.
    """
    return await service.send_family_request(requester_id=current_user["id"], request_data=request_data, db=db)


@router.get("/requests", summary="Get pending family requests")
async def get_requests(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Get all pending family requests — both incoming and outgoing."""
    return await service.get_requests(user_id=current_user["id"], db=db)


@router.post("/requests/{connection_id}/accept", summary="Accept a family request")
async def accept_request(
    connection_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Accept a pending family request. The requester will be notified via push + SMS."""
    return await service.accept_request(connection_id=connection_id, user_id=current_user["id"], db=db)


@router.post("/requests/{connection_id}/reject", summary="Reject a family request")
async def reject_request(
    connection_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Reject a pending family request. The requester will be notified via push + SMS."""
    return await service.reject_request(connection_id=connection_id, user_id=current_user["id"], db=db)


@router.get("/members", summary="List connected family members")
async def get_family_members(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> list[dict[str, Any]]:
    """List all accepted (connected) family members with their relation and access settings."""
    return await service.get_family_members(user_id=current_user["id"], db=db)


@router.patch("/members/{connection_id}", summary="Update family connection settings")
async def update_family_member(
    connection_id: int,
    data: FamilyRequestUpdate,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Update settings for a connected family member (e.g. toggle document access, permissions).

    Either party in the connection can call this endpoint.
    """
    return await service.update_member(
        connection_id=connection_id, user_id=current_user["id"], data=data, db=db
    )


@router.get("/members/{connection_id}/documents", summary="View family member's medical records")
async def get_member_documents(
    connection_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, Any]:
    """Access a connected family member's medical records.

    Returns all record types: hospital bookings, lab bookings, pharmacy orders,
    blood bank requests, and ambulance requests.

    Requires:
    - An active (connected) family connection.
    - `document_access_enabled = true` on the connection (default is true).
    """
    return await service.get_member_documents(
        connection_id=connection_id, viewer_id=current_user["id"], db=db
    )


@router.delete("/members/{connection_id}", summary="Remove a family member connection")
async def remove_family_member(
    connection_id: int,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    service: FamilyServiceDep,
) -> dict[str, str]:
    """Remove a family connection. Either party can remove the connection."""
    await service.remove_member(connection_id=connection_id, user_id=current_user["id"], db=db)
    return {"message": "Family member removed successfully"}
