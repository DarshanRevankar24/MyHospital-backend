import pytest

from src.modules.notification.sns_client import sns_client


@pytest.mark.unit
def test_sns_client_mock_push():
    endpoint_arn = sns_client.create_platform_endpoint("mock-fcm-token-12345")
    assert endpoint_arn.startswith("arn:aws:sns:")

    msg_id = sns_client.send_android_push(
        endpoint_arn=endpoint_arn,
        title="Test Push",
        body="Test Body Message",
        custom_data={"type": "test_alert"},
    )
    assert msg_id is not None


@pytest.mark.unit
def test_sns_client_mock_sms():
    msg_id = sns_client.send_sms(
        phone_number="+919876543210",
        message="Your OTP is 123456",
    )
    assert msg_id is not None
