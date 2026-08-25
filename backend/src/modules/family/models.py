from typing import Any, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import SoftDeleteMixin, TimestampMixin
from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..user.models import User


class FamilyConnection(Base, TimestampMixin, SoftDeleteMixin):
    """Model representing a connection between two family members."""

    __tablename__ = "family_connection"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    requester_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, connected, rejected
    permissions: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=lambda: {"access": "standard"})

    requester: Mapped["User"] = relationship(
        "User", foreign_keys=[requester_id], lazy="selectin", init=False
    )
    recipient: Mapped["User"] = relationship(
        "User", foreign_keys=[recipient_id], lazy="selectin", init=False
    )

    def __repr__(self) -> str:
        return f"<FamilyConnection(requester_id={self.requester_id}, recipient_id={self.recipient_id}, status={self.status})>"
