from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.medication.enums import MedicineType
from src.modules.medication.models import Medication
from src.modules.medication.tasks import check_and_send_medication_reminders

pytestmark = pytest.mark.asyncio


@pytest.mark.unit
async def test_medication_reminder_dispatch(db_session: AsyncSession, test_user: dict):
    """Test that check_and_send_medication_reminders sends notifications for matching time."""
    user_id = test_user["id"]
    today = date.today()

    med = Medication(
        user_id=user_id,
        created_by_user_id=user_id,
        name="Amoxicillin",
        medicine_type=MedicineType.TABLET,
        dosage="500mg",
        frequency="Daily",
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=5),
        reminder_times=["09:00", "21:00"],
        instructions="Take after food",
    )
    db_session.add(med)
    await db_session.commit()

    # Execute reminder check for 09:00 slot
    result = await check_and_send_medication_reminders(db=db_session, override_time="09:00")

    assert result["reminders_sent"] >= 1
    assert result["current_time"] == "09:00"

    # Test de-duplication: running again for 09:00 on same day should send 0 new reminders
    result_repeat = await check_and_send_medication_reminders(db=db_session, override_time="09:00")
    assert result_repeat["reminders_sent"] == 0


@pytest.mark.unit
async def test_medication_reminder_skips_non_matching_time(db_session: AsyncSession, test_user: dict):
    """Test that check_and_send_medication_reminders skips when current time does not match reminder_times."""
    user_id = test_user["id"]
    today = date.today()

    med = Medication(
        user_id=user_id,
        created_by_user_id=user_id,
        name="Paracetamol",
        medicine_type=MedicineType.TABLET,
        dosage="650mg",
        frequency="Daily",
        start_date=today,
        reminder_times=["14:00"],
    )
    db_session.add(med)
    await db_session.commit()

    # Execute for non-matching time (e.g. 10:00)
    result = await check_and_send_medication_reminders(db=db_session, override_time="10:00")
    assert result["reminders_sent"] == 0
