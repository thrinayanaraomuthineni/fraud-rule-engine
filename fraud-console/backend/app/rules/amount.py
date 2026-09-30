from ..config import settings
from .base import FraudRule


class UnusualAmountRule(FraudRule):
    name = "Unusual Amount"
    weight = settings.WEIGHT_AMOUNT

    def check(self, tx, history):
        if len(history) < settings.AMOUNT_MIN_HISTORY:
            return None  # not enough history to judge
        avg = sum(h.amount for h in history) / len(history)
        threshold = avg * settings.AMOUNT_MULTIPLIER
        if tx.amount > threshold:
            return (
                f"Amount {tx.currency} {tx.amount:,.0f} is {tx.amount / avg:.1f}× the account's historical "
                f"average of {avg:,.0f} (threshold {threshold:,.0f} = {settings.AMOUNT_MULTIPLIER:g}× average, "
                f"based on {len(history)} prior transactions)."
            )
