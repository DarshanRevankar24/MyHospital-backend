import json
import logging
from typing import Any

from ...infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 package not installed. AWS SNS integration will operate in mock mode.")


class SNSClient:
    """Wrapper class for AWS Simple Notification Service (SNS) operations."""

    def __init__(self) -> None:
        self.region = settings.AWS_REGION
        self.access_key = settings.AWS_ACCESS_KEY_ID
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.fcm_app_arn = settings.AWS_SNS_FCM_PLATFORM_APPLICATION_ARN

    def _get_client(self) -> Any:
        if not BOTO3_AVAILABLE:
            return None
        if not self.access_key or not self.secret_key:
            logger.warning("AWS Credentials not fully configured in settings.")
            return None
        return boto3.client(
            "sns",
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    def create_platform_endpoint(self, fcm_token: str, custom_user_data: str = "") -> str:
        """Register an Android FCM device token with AWS SNS Platform Application.

        Returns the generated EndpointArn string (or mock ARN if in test/mock mode).
        """
        client = self._get_client()
        if not client or not self.fcm_app_arn:
            logger.info(f"[MOCK SNS] Registered FCM token: {fcm_token[:15]}...")
            return f"arn:aws:sns:{self.region}:123456789012:endpoint/GCM/MyHospitalApp/{fcm_token[:10]}"

        try:
            response = client.create_platform_endpoint(
                PlatformApplicationArn=self.fcm_app_arn,
                Token=fcm_token,
                CustomUserData=custom_user_data,
            )
            endpoint_arn = str(response.get("EndpointArn", ""))
            logger.info(f"Created SNS Endpoint ARN: {endpoint_arn}")
            return endpoint_arn
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to create AWS SNS Platform Endpoint: {e}")
            raise RuntimeError(f"AWS SNS Endpoint Creation Error: {e}") from e

    def send_android_push(self, endpoint_arn: str, title: str, body: str, custom_data: dict[str, Any] | None = None) -> str:
        """Send Android Push Notification via AWS SNS Platform Endpoint (FCM/GCM JSON structure).

        Returns MessageId string.
        """
        client = self._get_client()

        # Build FCM / GCM payload structure for Android
        fcm_data = custom_data or {}
        fcm_payload = {
            "GCM": json.dumps(
                {
                    "notification": {
                        "title": title,
                        "body": body,
                        "sound": "default",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    },
                    "data": fcm_data,
                    "priority": "high",
                }
            )
        }
        message_json = json.dumps(fcm_payload)

        if not client:
            logger.info(f"[MOCK SNS PUSH] Sent to Endpoint: {endpoint_arn} | Title: {title} | Body: {body}")
            return "mock-sns-push-msg-id-12345"

        try:
            response = client.publish(
                TargetArn=endpoint_arn,
                Message=message_json,
                MessageStructure="json",
            )
            message_id = str(response.get("MessageId", ""))
            logger.info(f"Published SNS Push Notification MessageId: {message_id}")
            return message_id
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to publish SNS Push Notification: {e}")
            raise RuntimeError(f"AWS SNS Push Publish Error: {e}") from e

    def send_sms(self, phone_number: str, message: str) -> str:
        """Send direct SMS via AWS SNS.

        Returns MessageId string.
        """
        client = self._get_client()

        if not client:
            logger.info(f"[MOCK SNS SMS] Sent to {phone_number} | Message: {message}")
            return "mock-sns-sms-msg-id-67890"

        try:
            response = client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    "AWS.SNS.SMS.SMSType": {
                        "DataType": "String",
                        "StringValue": "Transactional",
                    }
                },
            )
            message_id = str(response.get("MessageId", ""))
            logger.info(f"Published SNS SMS to {phone_number}, MessageId: {message_id}")
            return message_id
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to publish SNS SMS: {e}")
            raise RuntimeError(f"AWS SNS SMS Publish Error: {e}") from e


sns_client = SNSClient()
