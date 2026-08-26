"""Pharmacy SQLAlchemy models."""

from decimal import Decimal

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base


class PharmacyProvider(Base, TimestampMixin):
    __tablename__ = "pharmacy_provider"

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
    is_delivery_available: Mapped[bool] = mapped_column(Boolean, default=False)
    delivery_radius_km: Mapped[float] = mapped_column(Float, default=5.0)
    is_24x7: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"PharmacyProvider({self.name})"


class Medicine(Base, TimestampMixin):
    __tablename__ = "medicine"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("pharmacy_provider.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(60), index=True)
    form: Mapped[str] = mapped_column(String(30))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    brand: Mapped[str | None] = mapped_column(String(80), default=None)
    generic_name: Mapped[str | None] = mapped_column(String(120), default=None)
    strength: Mapped[str | None] = mapped_column(String(40), default=None)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    requires_prescription: Mapped[bool] = mapped_column(Boolean, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"Medicine({self.name})"


class PharmacyOrder(Base, TimestampMixin):
    __tablename__ = "pharmacy_order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    order_ref: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("pharmacy_provider.id"), index=True)
    patient_name: Mapped[str] = mapped_column(String(80))
    patient_phone: Mapped[str] = mapped_column(String(15))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    items: Mapped[list] = mapped_column(JSON, default=list)  # [{medicine_id, quantity, unit_price}]
    delivery_type: Mapped[str] = mapped_column(String(20), default="pickup")
    delivery_address: Mapped[str | None] = mapped_column(String(300), default=None)
    prescription_url: Mapped[str | None] = mapped_column(String(300), default=None)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    def __repr__(self) -> str:
        return f"PharmacyOrder({self.order_ref}, {self.status})"
