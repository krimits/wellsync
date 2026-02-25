"""
Run this script once to create all database tables.

Usage:
    cd aeps-2026
    python -m backend.create_tables
"""
from backend.database import engine, Base

# Import all models so that Base.metadata is populated before create_all
import backend.models  # noqa: F401


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)


def main() -> None:
    print("Creating all tables...")
    create_all_tables()
    print("Done. Tables created:")
    for table_name in Base.metadata.tables:
        print(f"  - {table_name}")


if __name__ == "__main__":
    main()
