from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Date, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import SoftDeleteMixin, TimestampMixin
from ...infrastructure.database.session import Base
from .enums import MedicineType

if TYPE_CHECKING:
    from ..user.models import User


class Medication(Base, TimestampMixin, SoftDeleteMixin):
    """Model representing a user's medication schedule and pill reminders."""

    __tablename__ = "medication"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    medicine_type: Mapped[MedicineType] = mapped_column(SQLAlchemyEnum(MedicineType))
    dosage: Mapped[str] = mapped_column(String(100))
    frequency: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date)
    # Track if a family member added this
    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)

    instructions: Mapped[str | None] = mapped_column(String(500), default=None)
    end_date: Mapped[date | None] = mapped_column(Date, default=None)
    reminder_times: Mapped[list[str]] = mapped_column(JSON, default=list)  # list of HH:MM strings

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="selectin", init=False)
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id], lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"<Medication(id={self.id}, user_id={self.user_id}, name='{self.name}')>"
