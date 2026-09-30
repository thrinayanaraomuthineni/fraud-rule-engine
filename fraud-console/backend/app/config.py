import os

from dotenv import load_dotenv

load_dotenv()


def _env(key, default):
    return type(default)(os.getenv(key, default))


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fraud.db")
    # Velocity
    VELOCITY_LIMIT = _env("VELOCITY_LIMIT", 3)
    VELOCITY_WINDOW_MIN = _env("VELOCITY_WINDOW_MIN", 2.0)
    # Unusual amount
    AMOUNT_MULTIPLIER = _env("AMOUNT_MULTIPLIER", 3.0)
    AMOUNT_MIN_HISTORY = _env("AMOUNT_MIN_HISTORY", 3)
    # Impossible location
    MAX_TRAVEL_SPEED_KMH = _env("MAX_TRAVEL_SPEED_KMH", 900.0)
    MIN_DISTANCE_KM = _env("MIN_DISTANCE_KM", 100.0)
    # Risk contribution per rule
    WEIGHT_VELOCITY = _env("WEIGHT_VELOCITY", 30)
    WEIGHT_AMOUNT = _env("WEIGHT_AMOUNT", 30)
    WEIGHT_LOCATION = _env("WEIGHT_LOCATION", 40)
    # Risk levels: score >= threshold. Below MEDIUM is LOW.
    MEDIUM_THRESHOLD = _env("MEDIUM_THRESHOLD", 30)
    HIGH_THRESHOLD = _env("HIGH_THRESHOLD", 60)
    CRITICAL_THRESHOLD = _env("CRITICAL_THRESHOLD", 80)


settings = Settings()
