import enum


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class DevicePlatform(str, enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
