from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class RuleResult:
    rule: str
    triggered: bool
    reason: str
    risk: int = 0


class FraudRule(ABC):
    """Implement `check` and set `name` / `weight`. That is all a new rule needs."""

    name: str = "Rule"
    weight: int = 0

    @abstractmethod
    def check(self, tx, history) -> Optional[str]:
        """Return a human-readable reason if the rule triggers, otherwise None.

        `history` = the same account's earlier transactions, oldest first.
        """

    def evaluate(self, tx, history) -> RuleResult:
        reason = self.check(tx, history)
        if reason is None:
            return RuleResult(self.name, False, "No anomaly detected.")
        return RuleResult(self.name, True, reason, self.weight)
