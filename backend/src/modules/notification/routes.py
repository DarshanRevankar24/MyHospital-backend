from fastapi import APIRouter

from ...infrastructure.dependencies import AsyncSessionDep, CurrentUserDep
from .schemas import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationLogRead,
    SendPushNotification,
    SendSMSNotification,
)
from .service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/device-token", response_model=DeviceTokenResponse, summary="Register FCM Token for Android Push")
async def register_device_token(
    token_in: DeviceTokenCreate,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
) -> DeviceTokenResponse:
    """Register or update an Android FCM token for AWS SNS push notifications."""
    device = await NotificationService.register_device_token(db=db, user_id=current_user["id"], token_in=token_in)
    return DeviceTokenResponse.model_validate(device)


@router.post("/send-push", summary="Send Push Notification via AWS SNS")
async def send_push_notification(
    push_in: SendPushNotification,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
) -> list[NotificationLogRead]:
    """Send an Android push notification to a target user."""
    logs = await NotificationService.send_android_push(
        db=db,
        user_id=push_in.user_id,
        title=push_in.title,
        message=push_in.message,
        payload=push_in.payload,
        notification_type=push_in.notification_type,
    )
    return [NotificationLogRead.model_validate(log) for log in logs]


@router.post("/send-sms", summary="Send Custom SMS via AWS SNS")
async def send_sms_notification(
    sms_in: SendSMSNotification,
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
) -> NotificationLogRead:
    """Send a custom transactional SMS notification to a phone number or registered user."""
    log_entry = await NotificationService.send_sms(
        db=db,
        message=sms_in.message,
        phone_number=sms_in.phone_number,
        user_id=sms_in.user_id,
        notification_type=sms_in.notification_type,
    )
    return NotificationLogRead.model_validate(log_entry)


@router.get("/history", response_model=list[NotificationLogRead], summary="Get User Notification History")
async def get_notification_history(
    current_user: CurrentUserDep,
    db: AsyncSessionDep,
    limit: int = 50,
    offset: int = 0,
) -> list[NotificationLogRead]:
    """Retrieve history log of sent push and SMS notifications for the logged-in user."""
    logs = await NotificationService.get_user_notifications(db=db, user_id=current_user["id"], limit=limit, offset=offset)
    return [NotificationLogRead.model_validate(log) for log in logs]
