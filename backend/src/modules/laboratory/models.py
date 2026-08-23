"""Laboratory module SQLAlchemy models."""

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base


class LaboratoryProvider(Base, TimestampMixin):
    __tablename__ = "laboratory_provider"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(120))
    registration_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    address_line1: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(60), index=True)
    state: Mapped[str] = mapped_column(String(60))
    pincode: Mapped[str] = mapped_column(String(10))
    phone: Mapped[str] = mapped_column(String(15))
    
    address_line2: Mapped[str | None] = mapped_column(String(120), default=None)
    email: Mapped[str | None] = mapped_column(String(80), default=None)
    is_home_collection_available: Mapped[bool] = mapped_column(Boolean, default=False)
    home_collection_charge: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    logo_url: Mapped[str | None] = mapped_column(String(300), default=None)

    tests: Mapped[list["LabTest"]] = relationship("LabTest", back_populates="provider", lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"LaboratoryProvider({self.name}, {self.city})"


class LabTest(Base, TimestampMixin):
    __tablename__ = "lab_test"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("laboratory_provider.id"), index=True)
    test_name: Mapped[str] = mapped_column(String(120), index=True)
    test_code: Mapped[str] = mapped_column(String(30), index=True)
    category: Mapped[str] = mapped_column(String(40))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    description: Mapped[str | None] = mapped_column(String(500), default=None)
    discount_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=None)
    preparation_instructions: Mapped[str | None] = mapped_column(String(300), default=None)
    report_in_hours: Mapped[int] = mapped_column(Integer, default=24)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    provider: Mapped["LaboratoryProvider"] = relationship(
        "LaboratoryProvider", back_populates="tests", lazy="selectin", init=False
    )

    def __repr__(self) -> str:
        return f"LabTest({self.test_name})"


class LabBooking(Base, TimestampMixin):
    __tablename__ = "lab_booking"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    booking_ref: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("laboratory_provider.id"), index=True)
    patient_name: Mapped[str] = mapped_column(String(80))
    patient_phone: Mapped[str] = mapped_column(String(15))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    test_ids: Mapped[list] = mapped_column(JSON, default=list)
    collection_type: Mapped[str] = mapped_column(String(20), default="walk_in")
    collection_date: Mapped[str | None] = mapped_column(String(10), default=None)
    collection_time_slot: Mapped[str | None] = mapped_column(String(20), default=None)
    collection_address: Mapped[str | None] = mapped_column(String(300), default=None)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    report_url: Mapped[str | None] = mapped_column(String(300), default=None)

    def __repr__(self) -> str:
        return f"LabBooking({self.booking_ref}, {self.status})"
