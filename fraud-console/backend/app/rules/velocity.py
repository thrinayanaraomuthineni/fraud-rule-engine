from datetime import timedelta

from ..config import settings
from .base import FraudRule


class VelocityRule(FraudRule):
    name = "Velocity"
    weight = settings.WEIGHT_VELOCITY

    def check(self, tx, history):
        window = timedelta(minutes=settings.VELOCITY_WINDOW_MIN)
        count = 1 + sum(1 for h in history if tx.timestamp - h.timestamp <= window)
        if count > settings.VELOCITY_LIMIT:
            return (
                f"{count} transactions detected within {settings.VELOCITY_WINDOW_MIN:g} minutes; "
                f"configured limit is {settings.VELOCITY_LIMIT}."
            )
