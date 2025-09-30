"""Database utilities for SQLAlchemy integration."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.app.core.config import settings

Base = declarative_base()


def get_engine(url: str | None = None):  # pragma: no cover - thin wrapper
    return create_engine(url or settings.database_url, future=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


__all__ = ["Base", "get_engine", "SessionLocal"]
