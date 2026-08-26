from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import DevicePlatform


class DeviceTokenCreate(BaseModel):
    device_id: str = Field(..., description="Unique hardware or app instance identifier for the device.")
    fcm_token: str = Field(..., description="Firebase Cloud Messaging (FCM) registration token from Android client.")
    platform: str = Field(default=DevicePlatform.ANDROID, description="Platform type: android, ios, web.")


class DeviceTokenResponse(BaseModel):
    id: int
    user_id: int
    device_id: str
    platform: str
    fcm_token: str
    sns_endpoint_arn: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class SendPushNotification(BaseModel):
    user_id: int = Field(..., description="Target user ID to send the Android push notification to.")
    title: str = Field(..., description="Notification title.")
    message: str = Field(..., description="Notification body content.")
    payload: dict[str, Any] | None = Field(default=None, description="Optional custom data dictionary.")
    notification_type: str = Field(default="general", description="Categorization flag e.g. appointment, family, alert.")


class SendSMSNotification(BaseModel):
    phone_number: str | None = Field(default=None, description="E.164 formatted phone number (e.g. +919876543210).")
    user_id: int | None = Field(default=None, description="Optional user ID to resolve phone number from user profile.")
    message: str = Field(..., description="SMS message text.")
    notification_type: str = Field(default="general", description="Categorization flag e.g. otp, alert.")


class NotificationLogRead(BaseModel):
    id: int
    user_id: int | None
    channel: str
    notification_type: str
    title: str | None
    message: str
    phone_number: str | None
    sns_message_id: str | None
    status: str
    error_message: str | None
    payload: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceRead(BaseModel):
    push_enabled: bool
    sms_enabled: bool
    preferences: dict[str, Any] | None

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    push_enabled: bool | None = None
    sms_enabled: bool | None = None
    preferences: dict[str, Any] | None = None
