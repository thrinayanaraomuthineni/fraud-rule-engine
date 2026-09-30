from ..config import settings
from .base import FraudRule, RuleResult


class RuleEngine:
    """Runs whatever rules are registered. It knows nothing about specific rules."""

    def __init__(self, rules=()):
        self.rules: list[FraudRule] = list(rules)

    def register(self, rule: FraudRule) -> "RuleEngine":
        self.rules.append(rule)
        return self

    def evaluate(self, tx, history) -> list[RuleResult]:
        results = []
        for rule in self.rules:
            try:
                results.append(rule.evaluate(tx, history))
            except Exception as exc:  # one broken rule must not block the others
                results.append(RuleResult(rule.name, False, f"Rule failed to run: {exc}"))
        return results


def risk_level(score: int) -> str:
    if score >= settings.CRITICAL_THRESHOLD:
        return "CRITICAL"
    if score >= settings.HIGH_THRESHOLD:
        return "HIGH"
    if score >= settings.MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"
