"""Family service layer."""

from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.logging import get_logger
from ..ambulance.crud import crud_ambulance_requests
from ..blood_bank.crud import crud_blood_requests
from ..hospital.crud import crud_hospital_bookings
from ..laboratory.crud import crud_lab_bookings
from ..medication.crud import crud_medications
from ..medication.schemas import MedicationCreate, MedicationRead, MedicationUpdate
from ..notification.service import send_push_notification, send_sms_notification
from ..pharmacy.crud import crud_pharmacy_orders
from ..user.crud import crud_users
from ..user.schemas import UserRead
from .crud import crud_family_connection
from .schemas import FamilyConnectionRead, FamilyRequestCreate, FamilyRequestUpdate

logger = get_logger()


class FamilyService:
    """Service for managing family connections."""

    # ── Request flow ──────────────────────────────────────────────────────────

    async def send_family_request(
        self, requester_id: int, request_data: FamilyRequestCreate, db: AsyncSession
    ) -> dict[str, Any]:
        """Send a family connection request, storing the declared relation.

        Fires a push + SMS notification to the recipient after the row is created.
        """
        identifier = request_data.identifier

        # Look up recipient by username or phone
        recipient = await crud_users.get(db=db, schema_to_select=UserRead, username=identifier)
        if not recipient:
            recipient = await crud_users.get(db=db, schema_to_select=UserRead, phone_number=identifier)

        if not recipient:
            raise HTTPException(status_code=404, detail="User not found with the given identifier.")

        recipient_id = int(recipient["id"])

        if requester_id == recipient_id:
            raise HTTPException(status_code=400, detail="Cannot send a family request to yourself.")

        # Prevent duplicate connections
        existing_conn = await crud_family_connection.get(
            db=db, requester_id=requester_id, recipient_id=recipient_id, is_deleted=False
        )
        if existing_conn:
            raise HTTPException(
                status_code=400,
                detail=f"Connection already exists with status: {existing_conn['status']}",
            )

        # Fetch requester info for the notification message
        requester = await crud_users.get(db=db, schema_to_select=UserRead, id=requester_id)
        requester_name = requester["name"] if requester else "Someone"

        # Create the pending connection
        new_conn_data = {
            "requester_id": requester_id,
            "recipient_id": recipient_id,
            "status": "pending",
            "relation": request_data.relation,
            "permissions": {"access": "standard"},
            "document_access_enabled": True,
        }

        created_conn = await crud_family_connection.create(db=db, object=new_conn_data, schema_to_select=FamilyConnectionRead)
        if not created_conn:
            raise HTTPException(status_code=500, detail="Failed to create family connection request.")

        # ── Notify recipient ──────────────────────────────────────────────────
        relation_label = request_data.relation.value
        notif_title = "New Family Connection Request"
        notif_body = f"{requester_name} wants to connect with you as your {relation_label}. Open the app to accept or reject."
        if request_data.message:
            notif_body += f'\n\nPersonal note: "{request_data.message}"'

        try:
            await send_push_notification(
                db=db,
                user_id=recipient_id,
                title=notif_title,
                message=notif_body,
                notification_type="family_request",
                payload={
                    "connection_id": created_conn["id"],
                    "requester_id": requester_id,
                    "relation": relation_label,
                },
            )
        except Exception as exc:
            logger.warning(f"Push notification failed for family request (recipient={recipient_id}): {exc}")

        try:
            await send_sms_notification(
                db=db,
                user_id=recipient_id,
                message=f"{requester_name} sent you a family connection request "
                f"({relation_label}). Open the app to respond.",
                notification_type="family_request",
            )
        except Exception as exc:
            logger.warning(f"SMS notification failed for family request (recipient={recipient_id}): {exc}")

        logger.info(
            f"Family request sent: requester={requester_id}, recipient={recipient_id}, "
            f"relation={relation_label}, connection_id={created_conn['id']}"
        )
        return created_conn

    async def get_requests(self, user_id: int, db: AsyncSession) -> dict[str, Any]:
        """Get pending requests where user is recipient or requester."""
        incoming = await crud_family_connection.get_multi(
            db=db, recipient_id=user_id, status="pending", is_deleted=False, schema_to_select=FamilyConnectionRead
        )
        outgoing = await crud_family_connection.get_multi(
            db=db, requester_id=user_id, status="pending", is_deleted=False, schema_to_select=FamilyConnectionRead
        )
        inc_data = incoming.get("data", []) if isinstance(incoming, dict) else []
        out_data = outgoing.get("data", []) if isinstance(outgoing, dict) else []
        return {
            "incoming": inc_data,
            "outgoing": out_data,
        }

    async def accept_request(self, connection_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        """Accept a pending family request and notify the requester."""
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection request not found.")

        if conn["recipient_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to accept this request.")

        if conn["status"] != "pending":
            raise HTTPException(status_code=400, detail="Request is not in pending state.")

        updated = await crud_family_connection.update(
            db=db, id=connection_id, object={"status": "connected"}, schema_to_select=FamilyConnectionRead
        )
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to accept connection request.")

        # ── Notify requester ──────────────────────────────────────────────────
        acceptor = await crud_users.get(db=db, schema_to_select=UserRead, id=user_id)
        acceptor_name = acceptor["name"] if acceptor else "Your family member"
        requester_id = conn["requester_id"]

        try:
            await send_push_notification(
                db=db,
                user_id=requester_id,
                title="Family Request Accepted! 🎉",
                message=f"{acceptor_name} accepted your family connection request. "
                f"You can now view each other's health records.",
                notification_type="family_accepted",
                payload={"connection_id": connection_id},
            )
        except Exception as exc:
            logger.warning(f"Push notification failed for accept (requester={requester_id}): {exc}")

        try:
            await send_sms_notification(
                db=db,
                user_id=requester_id,
                message=f"[MyHospital] {acceptor_name} accepted your family connection request.",
                notification_type="family_accepted",
            )
        except Exception as exc:
            logger.warning(f"SMS notification failed for accept (requester={requester_id}): {exc}")

        return updated

    async def reject_request(self, connection_id: int, user_id: int, db: AsyncSession) -> dict[str, Any]:
        """Reject a pending family request and notify the requester."""
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection request not found.")

        if conn["recipient_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to reject this request.")

        updated = await crud_family_connection.update(
            db=db, id=connection_id, object={"status": "rejected"}, schema_to_select=FamilyConnectionRead
        )
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to reject connection request.")

        # ── Notify requester ──────────────────────────────────────────────────
        rejector = await crud_users.get(db=db, schema_to_select=UserRead, id=user_id)
        rejector_name = rejector["name"] if rejector else "The user"
        requester_id = conn["requester_id"]

        try:
            await send_push_notification(
                db=db,
                user_id=requester_id,
                title="Family Request Update",
                message=f"{rejector_name} declined your family connection request.",
                notification_type="family_rejected",
                payload={"connection_id": connection_id},
            )
        except Exception as exc:
            logger.warning(f"Push notification failed for reject (requester={requester_id}): {exc}")

        try:
            await send_sms_notification(
                db=db,
                user_id=requester_id,
                message=f"[MyHospital] {rejector_name} declined your family connection request.",
                notification_type="family_rejected",
            )
        except Exception as exc:
            logger.warning(f"SMS notification failed for reject (requester={requester_id}): {exc}")

        return updated

    async def get_family_members(self, user_id: int, db: AsyncSession) -> list[dict[str, Any]]:
        """List all connected family members."""
        requested = await crud_family_connection.get_multi(
            db=db, requester_id=user_id, status="connected", is_deleted=False, schema_to_select=FamilyConnectionRead
        )
        received = await crud_family_connection.get_multi(
            db=db, recipient_id=user_id, status="connected", is_deleted=False, schema_to_select=FamilyConnectionRead
        )

        req_data = requested.get("data", []) if isinstance(requested, dict) else []
        rec_data = received.get("data", []) if isinstance(received, dict) else []
        return req_data + rec_data

    async def update_member(
        self, connection_id: int, user_id: int, data: FamilyRequestUpdate, db: AsyncSession
    ) -> dict[str, Any]:
        """Update connection settings (permissions, document_access_enabled)."""
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found.")

        if conn["requester_id"] != user_id and conn["recipient_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this connection.")

        if conn["status"] != "connected":
            raise HTTPException(status_code=400, detail="Can only update an active (connected) family connection.")

        update_dict = data.model_dump(exclude_none=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update.")

        updated = await crud_family_connection.update(
            db=db, id=connection_id, object=update_dict, schema_to_select=FamilyConnectionRead
        )
        return updated

    async def remove_member(self, connection_id: int, user_id: int, db: AsyncSession) -> None:
        """Remove a family connection (soft delete)."""
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Connection not found.")

        if conn["requester_id"] != user_id and conn["recipient_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to remove this connection.")

        await crud_family_connection.delete(db=db, id=connection_id)

    # ── Document access ───────────────────────────────────────────────────────

    async def get_member_documents(self, connection_id: int, viewer_id: int, db: AsyncSession) -> dict[str, Any]:
        """Return the connected member's medical records if document access is enabled.

        The viewer must be either the requester or recipient of a connected, active
        connection with document_access_enabled=True.

        Returns a dict with: hospital_bookings, lab_bookings, pharmacy_orders,
        blood_requests, ambulance_requests.
        """
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Family connection not found.")

        if conn["requester_id"] != viewer_id and conn["recipient_id"] != viewer_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this connection's documents.")

        if conn["status"] != "connected":
            raise HTTPException(status_code=400, detail="Document access is only available for active connections.")

        if not conn.get("document_access_enabled", True):
            raise HTTPException(
                status_code=403,
                detail="Document access has been disabled for this connection.",
            )

        # The "other" user whose docs we want to see
        target_user_id = conn["recipient_id"] if viewer_id == conn["requester_id"] else conn["requester_id"]

        # ── Fetch records across all modules ─────────────────────────────────
        hospital_res = await crud_hospital_bookings.get_multi(db=db, user_id=target_user_id, is_deleted=False, limit=50)
        lab_res = await crud_lab_bookings.get_multi(db=db, user_id=target_user_id, is_deleted=False, limit=50)
        pharmacy_res = await crud_pharmacy_orders.get_multi(db=db, user_id=target_user_id, is_deleted=False, limit=50)
        blood_res = await crud_blood_requests.get_multi(db=db, user_id=target_user_id, is_deleted=False, limit=50)
        ambulance_res = await crud_ambulance_requests.get_multi(db=db, user_id=target_user_id, is_deleted=False, limit=50)

        def _data(res: Any) -> list:
            return res.get("data", []) if isinstance(res, dict) else []

        target_user = await crud_users.get(db=db, schema_to_select=UserRead, id=target_user_id)

        return {
            "connection_id": connection_id,
            "member": target_user,
            "relation": conn["relation"],
            "hospital_bookings": _data(hospital_res),
            "lab_bookings": _data(lab_res),
            "pharmacy_orders": _data(pharmacy_res),
            "blood_requests": _data(blood_res),
            "ambulance_requests": _data(ambulance_res),
        }

    async def _verify_medication_access(self, connection_id: int, viewer_id: int, db: AsyncSession) -> dict[str, Any]:
        """Helper to verify access to a member's medications."""
        conn = await crud_family_connection.get(db=db, id=connection_id, is_deleted=False)
        if not conn:
            raise HTTPException(status_code=404, detail="Family connection not found.")

        if conn["requester_id"] != viewer_id and conn["recipient_id"] != viewer_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this connection's medications.")

        if conn["status"] != "connected":
            raise HTTPException(status_code=400, detail="Medication access is only available for active connections.")

        if not conn.get("document_access_enabled", True):
            raise HTTPException(
                status_code=403,
                detail="Document/Medication access has been disabled for this connection.",
            )

        target_user_id = conn["recipient_id"] if viewer_id == conn["requester_id"] else conn["requester_id"]
        return {"conn": conn, "target_user_id": target_user_id}

    async def get_member_medications(
        self, connection_id: int, viewer_id: int, db: AsyncSession, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get medications of a connected family member."""
        access_data = await self._verify_medication_access(connection_id, viewer_id, db)
        target_user_id = access_data["target_user_id"]

        res = await crud_medications.get_multi(
            db=db, user_id=target_user_id, is_deleted=False, schema_to_select=MedicationRead, limit=limit
        )
        return res.get("data", []) if isinstance(res, dict) else []

    async def add_member_medication(
        self, connection_id: int, viewer_id: int, data: MedicationCreate, db: AsyncSession
    ) -> dict[str, Any]:
        """Add a medication for a connected family member."""
        access_data = await self._verify_medication_access(connection_id, viewer_id, db)
        target_user_id = access_data["target_user_id"]

        create_data = data.model_dump()
        create_data["user_id"] = target_user_id
        create_data["created_by_user_id"] = viewer_id

        created = await crud_medications.create(db=db, object=create_data, schema_to_select=MedicationRead)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create medication.")

        # Optional: Send push notification to target user about new medication added by family member
        try:
            viewer = await crud_users.get(db=db, schema_to_select=UserRead, id=viewer_id)
            viewer_name = viewer["name"] if viewer else "A family member"
            await send_push_notification(
                db=db,
                user_id=target_user_id,
                title="New Medication Added",
                message=f"{viewer_name} added a new medication '{data.name}' to your schedule.",
                notification_type="medication_added",
            )
        except Exception as exc:
            logger.warning(f"Push notification failed for medication added: {exc}")

        return created

    async def update_member_medication(
        self, connection_id: int, medication_id: int, viewer_id: int, data: MedicationUpdate, db: AsyncSession
    ) -> dict[str, Any]:
        """Update a medication for a connected family member."""
        access_data = await self._verify_medication_access(connection_id, viewer_id, db)
        target_user_id = access_data["target_user_id"]

        med = await crud_medications.get(db=db, id=medication_id, is_deleted=False)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found.")

        if med["user_id"] != target_user_id:
            raise HTTPException(status_code=403, detail="Medication does not belong to this family member.")

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update.")

        updated = await crud_medications.update(db=db, id=medication_id, object=update_data, schema_to_select=MedicationRead)
        return updated

    async def delete_member_medication(self, connection_id: int, medication_id: int, viewer_id: int, db: AsyncSession) -> None:
        """Delete a medication for a connected family member."""
        access_data = await self._verify_medication_access(connection_id, viewer_id, db)
        target_user_id = access_data["target_user_id"]

        med = await crud_medications.get(db=db, id=medication_id, is_deleted=False)
        if not med:
            raise HTTPException(status_code=404, detail="Medication not found.")

        if med["user_id"] != target_user_id:
            raise HTTPException(status_code=403, detail="Medication does not belong to this family member.")

        await crud_medications.delete(db=db, id=medication_id)
