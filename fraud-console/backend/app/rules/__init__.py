from .amount import UnusualAmountRule
from .engine import RuleEngine, risk_level  # noqa: F401
from .geography import ImpossibleLocationRule
from .velocity import VelocityRule

# To add a rule (e.g. DeviceMismatchRule): write the class, then add it to this list.
engine = RuleEngine([VelocityRule(), UnusualAmountRule(), ImpossibleLocationRule()])
