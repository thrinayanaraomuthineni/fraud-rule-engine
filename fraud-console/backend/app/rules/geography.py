from math import asin, cos, radians, sin, sqrt

from ..config import settings
from .base import FraudRule


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * 6371.0088 * asin(sqrt(a))


def _duration(seconds: float) -> str:
    return f"{seconds:.0f} seconds" if seconds < 90 else f"{seconds / 60:.0f} minutes"


class ImpossibleLocationRule(FraudRule):
    name = "Impossible Location"
    weight = settings.WEIGHT_LOCATION

    def check(self, tx, history):
        if not history:
            return None
        prev = max(history, key=lambda h: h.timestamp)
        km = haversine_km(prev.latitude, prev.longitude, tx.latitude, tx.longitude)
        seconds = max((tx.timestamp - prev.timestamp).total_seconds(), 1)
        speed = km / (seconds / 3600)
        if km >= settings.MIN_DISTANCE_KM and speed > settings.MAX_TRAVEL_SPEED_KMH:
            return (
                f"Transaction occurred {km:,.0f} km away ({prev.location} → {tx.location}) only "
                f"{_duration(seconds)} after the previous transaction. Required speed of {speed:,.0f} km/h "
                f"exceeds the {settings.MAX_TRAVEL_SPEED_KMH:,.0f} km/h limit."
            )
