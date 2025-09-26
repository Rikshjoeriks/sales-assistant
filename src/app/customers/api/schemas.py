"""Pydantic schemas for customer-facing endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator


class CustomerProfileCreate(BaseModel):
    name: str | None = None
    demographics: dict[str, Any] = Field(default_factory=dict)
    personality_assessment: dict[str, Any] = Field(default_factory=dict)
    communication_preferences: dict[str, Any] = Field(default_factory=dict)
    decision_factors: dict[str, Any] = Field(default_factory=dict)
    buying_context: dict[str, Any] = Field(default_factory=dict)
    sales_stage: str | None = None
    current_interest: str | None = None

    @validator("personality_assessment")
    def validate_personality(cls, value: dict[str, Any]) -> dict[str, Any]:
        disc = value.get("type")
        if disc and disc not in {"D", "I", "S", "C"}:
            raise ValueError("Personality assessment type must be one of D, I, S, C")
        return value


class CustomerProfileSummary(BaseModel):
    id: str
    name: str | None
    personality_type: str | None
    budget_range: str | None
    sales_stage: str
    interaction_count: int
    last_interaction: datetime | None
    profile_completeness: float

    class Config:
        from_attributes = True


class PaginationModel(BaseModel):
    limit: int
    offset: int
    has_more: bool


class CustomerListResponse(BaseModel):
    customers: list[CustomerProfileSummary]
    total_count: int
    pagination: PaginationModel


class ProfileSummaryModel(BaseModel):
    key_traits: list[str] = Field(default_factory=list)
    optimal_sales_approach: str | None = None
    potential_objections: list[str] = Field(default_factory=list)


class PersonalityProfileModel(BaseModel):
    type: str
    traits: dict[str, float]
    communication_style: str | None
    confidence: float


class CustomerProfileResponse(BaseModel):
    id: str
    name: str | None
    profile_completeness: float
    personality_type: str | None
    created_at: datetime
    recommendation_readiness: bool
    profile_summary: ProfileSummaryModel


class CustomerDetailResponse(BaseModel):
    id: str
    name: str | None
    demographics: dict[str, Any]
    personality_profile: PersonalityProfileModel
    communication_preferences: dict[str, Any]
    decision_factors: dict[str, Any]
    buying_context: dict[str, Any]
    interaction_history: list[dict[str, Any]]
    recommendations_generated: int
    average_recommendation_effectiveness: float
    created_at: datetime
    last_updated: datetime


class InteractionCreate(BaseModel):
    interaction_type: str
    date: datetime | None = None
    duration_minutes: int | None = None
    products_discussed: list[str] = Field(default_factory=list)
    customer_feedback: dict[str, Any] = Field(default_factory=dict)
    salesperson_notes: str | None = None
    outcome: str | None = None
    follow_up: dict[str, Any] = Field(default_factory=dict)
    recommendation_id: str | None = None
    sales_stage: str | None = None


class InteractionResponse(BaseModel):
    interaction_id: str
    customer_id: str
    recorded_at: datetime
    profile_updates: dict[str, Any] = Field(default_factory=dict)


class InteractionHistoryEntry(BaseModel):
    id: str
    date: datetime
    type: str
    duration_minutes: int | None
    outcome: str | None
    recommendation_used: dict[str, Any] | None


class InteractionHistoryResponse(BaseModel):
    customer_id: str
    interactions: list[InteractionHistoryEntry]
    interaction_summary: dict[str, Any]


class FollowUpSummary(BaseModel):
    interaction_id: str
    customer_id: str
    follow_up_type: str | None
    follow_up_at: datetime | None
    notes: str | None


class AnalyticsSummaryResponse(BaseModel):
    total_customers: int
    average_profile_score: float
    personality_distribution: dict[str, int]
    top_decision_factors: list[str]
    recent_follow_ups: list[FollowUpSummary]


__all__ = [
    "AnalyticsSummaryResponse",
    "CustomerDetailResponse",
    "CustomerListResponse",
    "CustomerProfileCreate",
    "CustomerProfileResponse",
    "CustomerProfileSummary",
    "FollowUpSummary",
    "InteractionCreate",
    "InteractionHistoryEntry",
    "InteractionHistoryResponse",
    "InteractionResponse",
    "PaginationModel",
    "PersonalityProfileModel",
    "ProfileSummaryModel",
]
