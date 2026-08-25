from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..user.crud import crud_users
from ..user.schemas import UserRead
from .crud import crud_family_connection
from .schemas import FamilyRequestCreate, FamilyConnectionRead
from ...infrastructure.logging import get_logger

logger = get_logger()

class FamilyService:
    """Service for managing family connections."""

    async def send_family_request(self, requester_id: int, request_data: FamilyRequestCreate, db: AsyncSession) -> dict[str, Any]:
        identifier = request_data.identifier
        
        # Look up user by username or phone
        recipient = await crud_users.get(db=db, schema_to_select=UserRead, username=identifier)
        if not recipient:
            recipient = await crud_users.get(db=db, schema_to_select=UserRead, phone_number=identifier)
            
        if not recipient:
            raise HTTPException(status_code=404, detail="User not found with the given identifier.")
            
        recipient_id = recipient["id"]
        
        if requester_id == recipient_id:
            raise HTTPException(status_code=400, detail="Cannot send a family request to yourself.")
            
        # Check if connection already exists
        existing_conn = await crud_family_connection.get(
            db=db, 
            requester_id=requester_id, 
            recipient_id=recipient_id,
            is_deleted=False
        )
        if existing_conn:
            raise HTTPException(status_code=400, detail=f"Connection already exists with status: {existing_conn['status']}")

        # Create pending connection
        new_conn_data = {
            "requester_id": requester_id,
            "recipient_id": recipient_id,
            "status": "pending",
            "permissions": {"access": "standard"}
        }
        
        created_conn = await crud_family_connection.create(db=db, object=new_conn_data)
        
        # MOCK sending notification
        logger.info(f"Verification link generated for {identifier}: https://app.myhospital.com/verify-family?conn={created_conn['id']}")
        
        return created_conn

    async def get_requests(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        """Get pending requests where user is recipient or requester."""
        incoming = await crud_family_connection.get_multi(
            db=db, recipient_id=user_id, status="pending", is_deleted=False
        )
        outgoing = await crud_family_connection.get_multi(
            db=db, requester_id=user_id, status="pending", is_deleted=False
        )
        return {
            "incoming": incoming.get("data", []),
            "outgoing": outgoing.get("data", [])
        }

    async def accept_request(self, connection_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection request not found.")
            
        if conn["recipient_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to accept this request.")
            
        if conn["status"] != "pending":
            raise HTTPException(status_code=400, detail="Request is not in pending state.")
            
        updated = await crud_family_connection.update(
            db=db, id=connection_id, object={"status": "connected"}
        )
        return updated

    async def reject_request(self, connection_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection request not found.")
            
        if conn["recipient_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to reject this request.")
            
        updated = await crud_family_connection.update(
            db=db, id=connection_id, object={"status": "rejected"}
        )
        return updated

    async def get_family_members(self, user_id: int, db: AsyncSession) -> list[dict[str, Any]]:
        # Members where I requested
        requested = await crud_family_connection.get_multi(
            db=db, requester_id=user_id, status="connected", is_deleted=False
        )
        # Members where I was recipient
        received = await crud_family_connection.get_multi(
            db=db, recipient_id=user_id, status="connected", is_deleted=False
        )
        
        all_connections = requested.get("data", []) + received.get("data", [])
        return all_connections

    async def remove_member(self, connection_id: int, user_id: int, db: AsyncSession) -> None:
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found.")
            
        if conn["requester_id"] != user_id and conn["recipient_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to remove this connection.")
            
        await crud_family_connection.delete(db=db, id=connection_id)
