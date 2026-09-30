"""Deterministic demo data. Run from backend/:  python -m app.seed   (resets the database)"""
import random
from datetime import datetime, timedelta

from .database import Base, SessionLocal, engine
from .models import Transaction
from .routes.transactions import score
from .services.notification import MockNotificationService

CITIES = {
    "Hyderabad": (17.385, 78.4867), "Mumbai": (19.076, 72.8777), "Bengaluru": (12.9716, 77.5946),
    "Delhi": (28.6139, 77.209), "London": (51.5074, -0.1278), "Singapore": (1.3521, 103.8198),
    "New York": (40.7128, -74.006),
}
NOW = datetime(2026, 9, 29, 10, 0)  # fixed anchor => identical data every run


def build():
    rnd, rows = random.Random(42), []
    add = lambda acc, ts, amt, city, status="PENDING", note=None: rows.append((acc, ts, amt, city, status, note))
    m, s = (lambda n: NOW + timedelta(minutes=n)), (lambda base, n: base + timedelta(seconds=n))

    # Normal history: six routine purchases per account over the previous days.
    for acc, city, base in [("ACC-101", "Hyderabad", 2200), ("ACC-102", "Mumbai", 2000),
                            ("ACC-103", "Bengaluru", 1500), ("ACC-204", "Hyderabad", 3200),
                            ("ACC-305", "Delhi", 2600), ("ACC-306", "Hyderabad", 1800)]:
        for d in range(6, 0, -1):
            ts = NOW - timedelta(days=d, hours=rnd.randint(0, 5), minutes=rnd.randint(0, 59))
            add(acc, ts, round(base * rnd.uniform(0.6, 1.4), -1), city)

    add("ACC-101", m(5), 2450, "Hyderabad")  # normal
    add("ACC-102", m(12), 48000, "Mumbai", "CLEARED",
        "Customer confirmed by phone: advance payment for a flat booking.")  # high value, cleared
    for i, amt in enumerate([1250, 980, 1310, 1190, 1275]):  # high velocity
        add("ACC-103", s(m(30), i * 20), amt, "Bengaluru",
            "REVIEWED" if i == 4 else "PENDING",
            "Checkout retries after a gateway timeout. No loss; no further action." if i == 4 else None)
    for i, amt in enumerate([2800, 3100, 2500, 3400]):  # burst, then impossible hop: triggers all rules
        add("ACC-204", s(m(60), i * 20), amt, "Hyderabad")
    add("ACC-204", s(m(60), 80), 85000, "London")
    add("ACC-305", m(90), 2200, "Delhi")
    add("ACC-305", m(105), 30000, "Singapore")  # impossible location + large amount
    add("ACC-306", m(120), 1900, "Hyderabad")
    add("ACC-306", m(140), 2100, "New York")  # impossible location only
    return sorted(rows, key=lambda r: r[1])


def main():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    notifier = MockNotificationService()  # seeding never calls AWS
    with SessionLocal() as db:
        for acc, ts, amount, city, status, note in build():
            lat, lon = CITIES[city]
            tx = Transaction(account_id=acc, amount=amount, timestamp=ts, latitude=lat,
                             longitude=lon, location=city)
            db.add(tx)
            db.flush()
            score(db, tx, notifier)
            if status != "PENDING":
                tx.review_status, tx.reviewer_note, tx.reviewed_at = status, note, ts + timedelta(hours=2)
            elif note:
                tx.reviewer_note = note
            db.commit()
        total = db.query(Transaction).count()
        flagged = db.query(Transaction).filter(Transaction.is_flagged).count()
    print(f"Seeded {total} transactions ({flagged} flagged).")


if __name__ == "__main__":
    main()
