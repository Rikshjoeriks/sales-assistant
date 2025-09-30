"""Customer profile search orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.app.customers.repositories.profile_repository import (
    CustomerProfileRepository,
    CustomerSummary,
)


@dataclass(slots=True)
class Pagination:
    limit: int
    offset: int
    has_more: bool


@dataclass(slots=True)
class CustomerSearchResult:
    customer_id: str
    name: str | None
    personality_type: str | None
    budget_range: str | None
    sales_stage: str
    interaction_count: int
    last_interaction: datetime | None
    profile_score: float


@dataclass(slots=True)
class CustomerSearchPage:
    customers: list[CustomerSearchResult]
    total: int
    pagination: Pagination


class CustomerSearchService:
    """Coordinate repository filtering and pagination for customer search."""

    def __init__(self, *, repository: CustomerProfileRepository) -> None:
        self._repository = repository

    def search(
        self,
        *,
        personality_type: str | None = None,
        budget_range: str | None = None,
        search: str | None = None,
        sales_stage: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> CustomerSearchPage:
        filters: dict[str, Any] = {}
        if personality_type:
            filters["personality_type"] = personality_type
        if budget_range:
            filters["budget_range"] = budget_range
        if search:
            filters["search"] = search
        if sales_stage:
            filters["sales_stage"] = sales_stage

        summaries, total = self._repository.search_profiles(filters=filters, limit=limit, offset=offset)
        customers = [self._to_result(summary) for summary in summaries]
        pagination = Pagination(limit=limit, offset=offset, has_more=(offset + len(customers)) < total)
        return CustomerSearchPage(customers=customers, total=total, pagination=pagination)

    def _to_result(self, summary: CustomerSummary) -> CustomerSearchResult:
        return CustomerSearchResult(
            customer_id=str(summary.customer_id),
            name=summary.name,
            personality_type=summary.personality_type,
            budget_range=summary.budget_range,
            sales_stage=summary.sales_stage,
            interaction_count=summary.interaction_count,
            last_interaction=summary.last_interaction_at,
            profile_score=summary.profile_score,
        )


__all__ = [
    "CustomerSearchService",
    "CustomerSearchPage",
    "CustomerSearchResult",
    "Pagination",
]
