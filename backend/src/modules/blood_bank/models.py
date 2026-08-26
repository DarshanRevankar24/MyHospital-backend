"""Blood Bank SQLAlchemy models."""

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base


class BloodBankProvider(Base, TimestampMixin):
    __tablename__ = "blood_bank_provider"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(120))
    license_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    address_line1: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(60), index=True)
    state: Mapped[str] = mapped_column(String(60))
    pincode: Mapped[str] = mapped_column(String(10))
    phone: Mapped[str] = mapped_column(String(15))

    address_line2: Mapped[str | None] = mapped_column(String(120), default=None)
    email: Mapped[str | None] = mapped_column(String(80), default=None)
    is_24x7: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"BloodBankProvider({self.name})"


class BloodStock(Base, TimestampMixin):
    __tablename__ = "blood_stock"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("blood_bank_provider.id"), index=True)
    blood_group: Mapped[str] = mapped_column(String(5), index=True)
    units_available: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"BloodStock({self.blood_group}: {self.units_available})"


class BloodRequest(Base, TimestampMixin):
    __tablename__ = "blood_request"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    request_ref: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("blood_bank_provider.id"), index=True)
    blood_group: Mapped[str] = mapped_column(String(5))
    units_required: Mapped[int] = mapped_column(Integer)
    patient_name: Mapped[str] = mapped_column(String(80))
    patient_contact: Mapped[str] = mapped_column(String(15))

    urgency: Mapped[str] = mapped_column(String(10), default="normal")
    patient_hospital: Mapped[str | None] = mapped_column(String(120), default=None)
    required_by_date: Mapped[str | None] = mapped_column(String(10), default=None)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    notes: Mapped[str | None] = mapped_column(String(500), default=None)

    def __repr__(self) -> str:
        return f"BloodRequest({self.request_ref}, {self.blood_group})"
