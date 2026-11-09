"""
YuvaAi - Database Module

Purpose:
Manages PostgreSQL connectivity and database sessions.
"""

from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.config import DATABASE_URL

#**********************************************************

# 1. DATABASE ENGINE

#**************************************************************

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

#**********************************************************

# 2. DATABASE SESSION

#**************************************************************

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

#**********************************************************

# 3. DECLARATIVE BASE

#**************************************************************

Base = declarative_base()

#**********************************************************

# 4. DECLARATIVE SESSION DEPENDENCY

#**************************************************************

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

#**********************************************************

# 5. DATABASE CONNECTION TEST

#******************************************************

def test_connection():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT version()")
            )

            version = result.scalar()

            print("PostgreSQL connected successfully!")
            print("Database:", engine.url.database)
            print("Version:", version)

            return True

    except Exception as error:

        print("Database connection failed!")
        print("Error:", error)

        return False
