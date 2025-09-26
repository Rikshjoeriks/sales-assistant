"""Dependency helpers for customer intelligence components."""
from __future__ import annotations

from functools import lru_cache
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.app.core.db import SessionLocal
from src.app.customers.repositories.interaction_repository import InteractionRepository
from src.app.customers.repositories.profile_repository import CustomerProfileRepository
from src.app.customers.services.decision_service import DecisionService
from src.app.customers.services.personality_engine import PersonalityEngine
from src.app.customers.services.search_service import CustomerSearchService


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@lru_cache(maxsize=1)
def get_personality_engine() -> PersonalityEngine:
    return PersonalityEngine()


@lru_cache(maxsize=1)
def get_decision_service() -> DecisionService:
    return DecisionService()


def get_profile_repository(session: Session = Depends(get_session)) -> CustomerProfileRepository:
    return CustomerProfileRepository(session=session)


def get_interaction_repository(
    session: Session = Depends(get_session),
    profile_repository: CustomerProfileRepository = Depends(get_profile_repository),
) -> InteractionRepository:
    return InteractionRepository(session=session, profile_repository=profile_repository)


def get_search_service(
    repository: CustomerProfileRepository = Depends(get_profile_repository),
) -> CustomerSearchService:
    return CustomerSearchService(repository=repository)


__all__ = [
    "get_decision_service",
    "get_interaction_repository",
    "get_personality_engine",
    "get_profile_repository",
    "get_search_service",
    "get_session",
]
