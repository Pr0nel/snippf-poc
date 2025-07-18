# app/infra/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://snippf:snippf@localhost:5432/snippf_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Session:
    """Proporciona una sesión SQLAlchemy (usar con Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()