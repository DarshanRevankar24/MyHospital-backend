from enum import StrEnum


class NotificationChannel(StrEnum):
    PUSH = "push"
    SMS = "sms"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class DevicePlatform(StrEnum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
