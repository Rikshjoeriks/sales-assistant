"""Customer search service tests."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TypedDict, cast

from src.app.customers.services.search_service import CustomerSearchService
from src.app.customers.repositories.profile_repository import CustomerProfileRepository


@dataclass
class _CustomerSummary:
    id: str
    name: str
    personality_type: str
    budget_range: str
    sales_stage: str
    interaction_count: int
    last_interaction_at: datetime | None
    profile_score: float


class _SearchCall(TypedDict):
    filters: dict[str, object]
    limit: int
    offset: int


class _FakeRepository:
    def __init__(self) -> None:
        self.calls: list[_SearchCall] = []
        self._results = [
            _CustomerSummary(
                id="cust-1",
                name="Test Customer",
                personality_type="D",
                budget_range="40k_60k",
                sales_stage="presentation",
                interaction_count=3,
                last_interaction_at=datetime.now(tz=timezone.utc),
                profile_score=0.82,
            )
        ]

    def search(self, *, filters: dict[str, object], limit: int, offset: int):
        self.calls.append(_SearchCall(filters=filters, limit=limit, offset=offset))
        return self._results, len(self._results)


def test_search_service_forwards_filters_and_wraps_results() -> None:
    repo = _FakeRepository()
    service = CustomerSearchService(repository=cast(CustomerProfileRepository, repo))

    page = service.search(
        personality_type="D",
        budget_range="40k_60k",
        search="engineer",
        sales_stage="presentation",
        limit=10,
        offset=0,
    )

    assert repo.calls[0]["filters"]["personality_type"] == "D"
    assert repo.calls[0]["filters"]["budget_range"] == "40k_60k"
    assert repo.calls[0]["filters"]["search"] == "engineer"
    assert page.total == 1
    assert page.customers[0].name == "Test Customer"
    assert page.customers[0].profile_score == 0.82
    assert page.pagination.limit == 10
    assert page.pagination.has_more is False
