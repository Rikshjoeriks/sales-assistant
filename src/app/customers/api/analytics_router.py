"""Analytics endpoints for customer intelligence."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.app.customers.api.schemas import AnalyticsSummaryResponse, FollowUpSummary
from src.app.customers.dependencies import get_interaction_repository, get_profile_repository
from src.app.customers.repositories.interaction_repository import InteractionRepository
from src.app.customers.repositories.profile_repository import CustomerProfileRepository

router = APIRouter(prefix="/api/v1/customers/analytics", tags=["Customer Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary(
    repository: CustomerProfileRepository = Depends(get_profile_repository),
    interactions: InteractionRepository = Depends(get_interaction_repository),
) -> AnalyticsSummaryResponse:
    """Aggregate customer analytics for dashboards and monitoring."""
    return AnalyticsSummaryResponse(
        total_customers=repository.total_customers(),
        average_profile_score=repository.average_profile_score(),
        personality_distribution=repository.personality_distribution(),
        top_decision_factors=repository.top_decision_factors(),
        recent_follow_ups=[
            FollowUpSummary(
                interaction_id=str(item.interaction_id),
                customer_id=str(item.customer_id),
                follow_up_type=item.follow_up_type,
                follow_up_at=item.follow_up_at,
                notes=item.notes,
            )
            for item in interactions.recent_follow_ups()
        ],
    )


__all__ = ["router"]
