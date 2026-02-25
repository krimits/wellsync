"""
Seed script — inserts demo user + 20 days of check-ins, workouts, meals.

Usage:
    cd /path/to/wellsync
    python -m backend.seed
"""
from datetime import date, timedelta
import random

from backend.database import SessionLocal
from backend.create_tables import create_all_tables
from backend.models.user import User
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.meal import Meal
from backend.routers.auth import hash_password

random.seed(42)


def seed():
    create_all_tables()
    db = SessionLocal()
    try:
        # Demo user
        email = "demo@wellsync.app"
        if not db.query(User).filter(User.email == email).first():
            user = User(
                email=email,
                name="Alex Demo",
                password_hash=hash_password("wellsync123"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user: {email} / wellsync123")
        else:
            user = db.query(User).filter(User.email == email).first()
            print(f"User exists: {email}")

        today = date.today()
        workout_types = ["running", "cycling", "weightlifting", "yoga", "hiit", "walking"]

        for i in range(20, 0, -1):
            d = today - timedelta(days=i)

            if not db.query(CheckIn).filter(CheckIn.user_id == user.id, CheckIn.date == d).first():
                sleep_h = round(random.uniform(5.5, 8.5), 1)
                checkin = CheckIn(
                    user_id=user.id,
                    date=d,
                    sleep_hours=sleep_h,
                    sleep_quality=random.randint(2, 5),
                    mood=random.randint(2, 5),
                    energy=random.randint(2, 5),
                    stress=random.randint(1, 4),
                )
                db.add(checkin)

            if i % 2 == 0 and not db.query(Workout).filter(Workout.user_id == user.id, Workout.date == d).first():
                db.add(Workout(
                    user_id=user.id,
                    date=d,
                    type=random.choice(workout_types),
                    duration_min=random.randint(20, 60),
                    rpe=random.randint(4, 8),
                ))

            for mtype in ["breakfast", "lunch", "dinner"]:
                if not db.query(Meal).filter(
                    Meal.user_id == user.id, Meal.date == d, Meal.meal_type == mtype
                ).first():
                    db.add(Meal(
                        user_id=user.id, date=d,
                        meal_type=mtype,
                        quality=random.randint(2, 5),
                        notes=None,
                    ))

        db.commit()
        print("Seed complete: 20 days of demo data inserted.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
