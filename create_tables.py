from backend.database import engine, Base
from backend.models import Conversation, Message, UsageRecord, UsageEvent


def create_tables():

    print("Creating YuvaAI database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")

    print("\nAvailable tables:")

    for table in Base.metadata.sorted_tables:
        print("-", table.name)


if __name__ == "__main__":
    create_tables()