#!/usr/bin/env python3
"""Taskiq worker entry point."""

from ...modules.medication.tasks import check_and_send_medication_reminders
from .brokers import default_broker

__all__ = ["default_broker", "check_and_send_medication_reminders"]

if __name__ == "__main__":
    # Run with: python -m taskiq worker infrastructure.taskiq.worker:default_broker
    pass
