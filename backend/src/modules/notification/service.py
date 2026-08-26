import logging
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.models import User
from .enums import NotificationChannel, NotificationStatus
from .models import DeviceToken, NotificationLog, NotificationPreference
from .schemas import DeviceTokenCreate
from .sns_client import sns_client

logger = logging.getLogger(__name__)


class NotificationService:
    """Service handling Android Push Notifications and SMS dispatch via AWS SNS."""

    @staticmethod
    async def register_device_token(
        db: AsyncSession, user_id: int, token_in: DeviceTokenCreate
    ) -> DeviceToken:
        """Register or update a user's Android FCM device token and register with SNS."""
        # Query existing token for this user & device_id
        result = await db.execute(
            select(DeviceToken).where(
                DeviceToken.user_id == user_id,
                DeviceToken.device_id == token_in.device_id,
                DeviceToken.is_deleted == False,  # noqa: E712
            )
        )
        existing_device = result.scalars().first()

        # Register endpoint with AWS SNS Platform Application
        endpoint_arn = sns_client.create_platform_endpoint(
            fcm_token=token_in.fcm_token, custom_user_data=f"user_{user_id}"
        )

        if existing_device:
            existing_device.fcm_token = token_in.fcm_token
            existing_device.platform = token_in.platform
            existing_device.sns_endpoint_arn = endpoint_arn
            existing_device.is_active = True
            await db.commit()
            await db.refresh(existing_device)
            return existing_device

        new_device = DeviceToken(
            user_id=user_id,
            device_id=token_in.device_id,
            fcm_token=token_in.fcm_token,
            platform=token_in.platform,
            sns_endpoint_arn=endpoint_arn,
            is_active=True,
        )
        db.add(new_device)
        await db.commit()
        await db.refresh(new_device)
        return new_device

    @staticmethod
    async def send_android_push(
        db: AsyncSession,
        user_id: int,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
        notification_type: str = "general",
    ) -> list[NotificationLog]:
        """Send an Android push notification to all active devices of a user via AWS SNS."""
        # Check user preferences
        pref_res = await db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        pref = pref_res.scalars().first()
        if pref and not pref.push_enabled:
            logger.info(f"Push notifications disabled for user_id={user_id}. Skipping.")
            return []

        # Find user active device tokens
        devices_res = await db.execute(
            select(DeviceToken).where(
                DeviceToken.user_id == user_id,
                DeviceToken.is_active == True,  # noqa: E712
                DeviceToken.is_deleted == False,  # noqa: E712
            )
        )
        devices = devices_res.scalars().all()

        if not devices:
            logger.warning(f"No active registered device tokens found for user_id={user_id}")
            # Create a log entry indicating no device registered
            log_entry = NotificationLog(
                channel=NotificationChannel.PUSH,
                message=message,
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                status=NotificationStatus.FAILED,
                error_message="No active device token registered for user.",
                payload=payload,
            )
            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)
            return [log_entry]

        logs: list[NotificationLog] = []
        for device in devices:
            target_arn = device.sns_endpoint_arn
            if not target_arn:
                target_arn = sns_client.create_platform_endpoint(device.fcm_token)
                device.sns_endpoint_arn = target_arn

            log_entry = NotificationLog(
                channel=NotificationChannel.PUSH,
                message=message,
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                status=NotificationStatus.PENDING,
                payload=payload,
            )
            db.add(log_entry)
            await db.flush()  # populate log_entry.id

            try:
                msg_id = sns_client.send_android_push(
                    endpoint_arn=target_arn,
                    title=title,
                    body=message,
                    custom_data=payload,
                )
                log_entry.sns_message_id = msg_id
                log_entry.status = NotificationStatus.SENT
            except Exception as exc:
                logger.error(f"Error sending push notification to endpoint {target_arn}: {exc}")
                log_entry.status = NotificationStatus.FAILED
                log_entry.error_message = str(exc)

            logs.append(log_entry)

        await db.commit()
        for log in logs:
            await db.refresh(log)
        return logs

    @staticmethod
    async def send_sms(
        db: AsyncSession,
        message: str,
        phone_number: str | None = None,
        user_id: int | None = None,
        notification_type: str = "general",
    ) -> NotificationLog:
        """Send a custom SMS notification via AWS SNS to a phone number or resolved user phone."""
        target_phone = phone_number

        if not target_phone and user_id:
            user_res = await db.execute(select(User).where(User.id == user_id))
            user = user_res.scalars().first()
            if user:
                target_phone = user.phone_number

        if not target_phone:
            raise ValueError("Phone number is required for sending SMS notification.")

        # Check preference if user_id is provided
        if user_id:
            pref_res = await db.execute(
                select(NotificationPreference).where(NotificationPreference.user_id == user_id)
            )
            pref = pref_res.scalars().first()
            if pref and not pref.sms_enabled:
                logger.info(f"SMS notifications disabled for user_id={user_id}. Skipping.")
                log_entry = NotificationLog(
                    channel=NotificationChannel.SMS,
                    message=message,
                    user_id=user_id,
                    notification_type=notification_type,
                    phone_number=target_phone,
                    status=NotificationStatus.FAILED,
                    error_message="SMS disabled by user preferences.",
                )
                db.add(log_entry)
                await db.commit()
                await db.refresh(log_entry)
                return log_entry

        log_entry = NotificationLog(
            channel=NotificationChannel.SMS,
            message=message,
            user_id=user_id,
            notification_type=notification_type,
            phone_number=target_phone,
            status=NotificationStatus.PENDING,
        )
        db.add(log_entry)
        await db.flush()

        try:
            msg_id = sns_client.send_sms(phone_number=target_phone, message=message)
            log_entry.sns_message_id = msg_id
            log_entry.status = NotificationStatus.SENT
        except Exception as exc:
            logger.error(f"Error sending SMS to {target_phone}: {exc}")
            log_entry.status = NotificationStatus.FAILED
            log_entry.error_message = str(exc)

        await db.commit()
        await db.refresh(log_entry)
        return log_entry

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession, user_id: int, limit: int = 50, offset: int = 0
    ) -> list[NotificationLog]:
        """Fetch notification history log for a specific user."""
        result = await db.execute(
            select(NotificationLog)
            .where(
                NotificationLog.user_id == user_id,
                NotificationLog.is_deleted == False,  # noqa: E712
            )
            .order_by(NotificationLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())


# Quick top-level helper functions for clean imports across services:
# Example: from backend.src.modules.notification.service import send_push_notification
send_push_notification = NotificationService.send_android_push
send_sms_notification = NotificationService.send_sms
