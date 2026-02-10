"""
Dive AI Database Configuration
SQLAlchemy setup for chat persistence
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./dive_ai.db'
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from database.models import ChatSession, ChatMessage, AlgorithmExecution
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
