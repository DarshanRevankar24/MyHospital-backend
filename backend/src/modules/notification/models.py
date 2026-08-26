from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import SoftDeleteMixin, TimestampMixin
from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..user.models import User


class DeviceToken(Base, TimestampMixin, SoftDeleteMixin):
    """Model representing registered user device tokens for push notifications (e.g. Android FCM)."""

    __tablename__ = "device_token"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    # ── Non-default fields first ─────────────────────────────────────────────
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    fcm_token: Mapped[str] = mapped_column(String(500))

    # ── Fields with defaults ─────────────────────────────────────────────────
    platform: Mapped[str] = mapped_column(String(20), default="android")  # android, ios, web
    sns_endpoint_arn: Mapped[str | None] = mapped_column(String(500), default=None)
    is_active: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"<DeviceToken(user_id={self.user_id}, platform={self.platform}, device_id={self.device_id})>"


class NotificationLog(Base, TimestampMixin, SoftDeleteMixin):
    """Model tracking sent and failed notifications (Push & SMS)."""

    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    # ── Non-default fields first ─────────────────────────────────────────────
    channel: Mapped[str] = mapped_column(String(20))  # push, sms
    message: Mapped[str] = mapped_column(String(1000))

    # ── Fields with defaults ─────────────────────────────────────────────────
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), index=True, default=None)
    notification_type: Mapped[str] = mapped_column(String(50), default="general")  # e.g., otp, appointment, reminder
    title: Mapped[str | None] = mapped_column(String(200), default=None)
    phone_number: Mapped[str | None] = mapped_column(String(20), default=None)
    sns_message_id: Mapped[str | None] = mapped_column(String(100), default=None)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, sent, failed
    error_message: Mapped[str | None] = mapped_column(String, default=None)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id], lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"<NotificationLog(id={self.id}, channel={self.channel}, status={self.status})>"


class NotificationPreference(Base, TimestampMixin, SoftDeleteMixin):
    """Model storing user notification preferences."""

    __tablename__ = "notification_preference"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    # ── Non-default fields first ─────────────────────────────────────────────
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), unique=True, index=True)

    # ── Fields with defaults ─────────────────────────────────────────────────
    push_enabled: Mapped[bool] = mapped_column(default=True)
    sms_enabled: Mapped[bool] = mapped_column(default=True)
    preferences: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, default=lambda: {"promotional": True, "transactional": True}
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"<NotificationPreference(user_id={self.user_id}, push={self.push_enabled}, sms={self.sms_enabled})>"
