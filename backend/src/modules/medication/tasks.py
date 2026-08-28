"""Taskiq background tasks for medication reminders."""

import logging
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import select

from ...infrastructure.taskiq import default_broker
from ...infrastructure.taskiq.deps import DBSession
from ..notification.models import NotificationLog
from ..notification.service import send_push_notification, send_sms_notification
from .models import Medication

logger = logging.getLogger(__name__)


@default_broker.task(name="check_and_send_medication_reminders")
async def check_and_send_medication_reminders(
    db: DBSession,
    override_time: str | None = None,
) -> dict[str, Any]:
    """Check all active medication schedules and dispatch push/SMS reminders for matching time slots.

    Args:
        db: Database session injected by Taskiq.
        override_time: Optional HH:MM string to override current system time (useful for manual or test triggers).

    Returns:
        Summary dict containing time checked, total active medications, and count of sent reminders.
    """
    now = datetime.now()
    today = date.today()
    current_time_str = override_time or now.strftime("%H:%M")

    logger.info(f"Running medication reminder check for time={current_time_str}, date={today}")

    # Query active medications where start_date <= today and (end_date is None or end_date >= today)
    stmt = select(Medication).where(
        Medication.is_deleted == False,  # noqa: E712
        Medication.start_date <= today,
        (Medication.end_date == None) | (Medication.end_date >= today),  # noqa: E711
    )
    result = await db.execute(stmt)
    medications = result.scalars().all()

    reminders_sent = 0

    for med in medications:
        reminder_times = med.reminder_times or []
        if current_time_str not in reminder_times:
            continue

        # Check for deduplication: has a reminder notification already been created today for this medication & time?
        log_stmt = select(NotificationLog).where(
            NotificationLog.user_id == med.user_id,
            NotificationLog.notification_type == "medication_reminder",
            NotificationLog.created_at >= datetime.combine(today, time.min),
        )
        logs_res = await db.execute(log_stmt)
        existing_logs = logs_res.scalars().all()

        already_sent = False
        for log in existing_logs:
            if (
                log.payload
                and log.payload.get("medication_id") == med.id
                and log.payload.get("reminder_time") == current_time_str
            ):
                already_sent = True
                break

        if already_sent:
            logger.info(f"Reminder for medication_id={med.id} at {current_time_str} already sent today. Skipping.")
            continue

        med_type_str = med.medicine_type.value if hasattr(med.medicine_type, "value") else str(med.medicine_type)

        # 1. Dispatch Push Notification
        title = f"Pill Reminder: {med.name} 💊"
        body = f"Time to take your {med_type_str} ({med.dosage})."
        if med.instructions:
            body += f" Note: {med.instructions}"

        payload = {
            "medication_id": med.id,
            "reminder_time": current_time_str,
            "dosage": med.dosage,
            "medicine_type": med_type_str,
        }

        try:
            await send_push_notification(
                db=db,
                user_id=med.user_id,
                title=title,
                message=body,
                notification_type="medication_reminder",
                payload=payload,
            )
        except Exception as exc:
            logger.error(f"Failed to send push reminder for medication_id={med.id}: {exc}")

        # 2. Dispatch SMS Notification
        sms_message = f"[MyHospital] Reminder: Take your medicine '{med.name}' ({med.dosage}) now."
        try:
            await send_sms_notification(
                db=db,
                user_id=med.user_id,
                message=sms_message,
                notification_type="medication_reminder",
            )
        except Exception as exc:
            logger.error(f"Failed to send SMS reminder for medication_id={med.id}: {exc}")

        reminders_sent += 1

    logger.info(f"Completed medication reminder check: sent {reminders_sent} reminder(s) for {current_time_str}")
    return {
        "current_time": current_time_str,
        "date": str(today),
        "total_active_medications": len(medications),
        "reminders_sent": reminders_sent,
    }
