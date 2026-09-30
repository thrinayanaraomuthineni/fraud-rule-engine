import logging
import os
from abc import ABC, abstractmethod

log = logging.getLogger("notifications")
AWS_VARS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "SNS_TOPIC_ARN")


class NotificationService(ABC):
    kind = ""

    @abstractmethod
    def send(self, subject: str, message: str) -> None: ...


class MockNotificationService(NotificationService):
    """Local fallback: logs the alert instead of calling AWS."""

    kind = "MOCK"

    def send(self, subject, message):
        log.warning("[MOCK NOTIFICATION] %s\n%s", subject, message)


class AWSNotificationService(NotificationService):
    """Publishes to SNS. Credentials come from the environment (read by boto3)."""

    kind = "AWS"

    def __init__(self):
        import boto3

        self.topic_arn = os.environ["SNS_TOPIC_ARN"]
        self.client = boto3.client("sns", region_name=os.environ["AWS_REGION"])

    def send(self, subject, message):
        self.client.publish(TopicArn=self.topic_arn, Subject=subject[:100], Message=message)


def aws_configured() -> bool:
    return all(os.getenv(k) for k in AWS_VARS)


def get_notifier() -> NotificationService:
    if aws_configured():
        try:
            return AWSNotificationService()
        except Exception as exc:
            log.warning("AWS notifier unavailable (%s); using mock.", exc)
    return MockNotificationService()


def notify_high_risk(tx, notifier: NotificationService = None) -> str:
    """Send an alert. Never raises; returns SENT_AWS, SENT_MOCK or FAILED."""
    try:
        notifier = notifier or get_notifier()
        reasons = "\n".join(f"- {f.rule} (+{f.risk}): {f.reason}" for f in tx.flags)
        notifier.send(
            f"[Fraud review] {tx.risk_level} risk: TX-{tx.id:04d} on {tx.account_id}",
            f"Transaction TX-{tx.id:04d} ({tx.currency} {tx.amount:,.0f}, {tx.location}) scored "
            f"{tx.risk_score}/100.\n{reasons}\n\nThis transaction requires investigation; "
            "it is not proof of fraud.",
        )
        return f"SENT_{notifier.kind}"
    except Exception as exc:
        log.error("High-risk notification failed: %s", exc)
        return "FAILED"
