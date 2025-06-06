import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Create SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
# Updated for Python 3.13 compatibility - using declarative_base from sqlalchemy.orm
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
