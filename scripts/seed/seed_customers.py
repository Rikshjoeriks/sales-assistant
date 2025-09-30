"""Seed script to bootstrap customer intelligence data."""
from __future__ import annotations

import datetime as dt
from dataclasses import asdict
from typing import Any, Iterable, Sequence

from src.app.core.db import SessionLocal
from src.app.customers.repositories.interaction_repository import InteractionRepository
from src.app.customers.repositories.profile_repository import CustomerProfileRepository
from src.app.customers.services.decision_service import DecisionService
from src.app.customers.services.personality_engine import PersonalityEngine
from src.app.customers.services.summary_service import (
    build_profile_summary,
    profile_to_evaluation_payload,
)


def _default_samples(now: dt.datetime) -> list[dict[str, Any]]:
    """Generate representative customer payloads with interactions."""
    return [
        {
            "profile": {
                "name": "Alex Rivera",
                "demographics": {
                    "age": 38,
                    "profession": "Sales Director",
                    "location": "Seattle, WA",
                },
                "personality_assessment": {"type": "D", "confidence": 0.82},
                "communication_preferences": {"style": "direct", "preferred_channels": ["email"]},
                "decision_factors": {
                    "primary": ["performance", "technology"],
                    "secondary": ["status"],
                    "deal_breakers": ["slow_delivery"],
                },
                "buying_context": {
                    "budget_range": "50k_70k",
                    "timeline": "within_1_month",
                    "current_vehicle": "2019 BMW 3 Series",
                },
                "sales_stage": "presentation",
                "current_interest": "2025 Apex Sport",
            },
            "interactions": [
                {
                    "interaction_type": "showroom_visit",
                    "date": (now - dt.timedelta(days=3)).isoformat(),
                    "duration_minutes": 45,
                    "products_discussed": ["2025 Apex Sport", "2025 Apex Sport Touring"],
                    "customer_feedback": {
                        "interest_level": "high",
                        "primary_concerns": ["delivery_time"],
                        "positive_responses": ["acceleration", "tech_suite"],
                    },
                    "salesperson_notes": "Enthusiastic about performance packages.",
                    "outcome": "interested",
                    "follow_up": {
                        "required": True,
                        "type": "phone_call",
                        "date": (now + dt.timedelta(days=2)).isoformat(),
                    },
                    "sales_stage": "negotiation",
                }
            ],
        },
        {
            "profile": {
                "name": "Morgan Lee",
                "demographics": {
                    "age": 33,
                    "profession": "UX Designer",
                    "location": "Portland, OR",
                },
                "personality_assessment": {"type": "I", "confidence": 0.76},
                "communication_preferences": {"style": "collaborative", "preferred_channels": ["sms", "phone"]},
                "decision_factors": {
                    "primary": ["community", "design"],
                    "secondary": ["technology"],
                    "deal_breakers": ["poor_support"],
                },
                "buying_context": {
                    "budget_range": "35k_45k",
                    "timeline": "within_2_months",
                    "current_vehicle": "2017 Honda HR-V",
                },
                "sales_stage": "prospecting",
                "current_interest": "2025 Terra Crossover",
            },
            "interactions": [
                {
                    "interaction_type": "virtual_consultation",
                    "date": (now - dt.timedelta(days=7)).isoformat(),
                    "duration_minutes": 30,
                    "products_discussed": ["2025 Terra Crossover"],
                    "customer_feedback": {
                        "interest_level": "medium",
                        "primary_concerns": ["monthly_payment"],
                        "positive_responses": ["interior_design"],
                    },
                    "salesperson_notes": "Wants to see community testimonials and financing options.",
                    "outcome": "follow_up",
                    "follow_up": {
                        "required": True,
                        "type": "email",
                        "date": (now + dt.timedelta(days=5)).isoformat(),
                    },
                    "sales_stage": "presentation",
                }
            ],
        },
        {
            "profile": {
                "name": "Jordan Patel",
                "demographics": {
                    "age": 41,
                    "profession": "Systems Engineer",
                    "location": "San Jose, CA",
                },
                "personality_assessment": {"type": "C", "confidence": 0.9},
                "communication_preferences": {"style": "analytical", "preferred_channels": ["email"]},
                "decision_factors": {
                    "primary": ["safety", "efficiency"],
                    "secondary": ["total_cost_of_ownership"],
                    "deal_breakers": ["poor_reliability"],
                },
                "buying_context": {
                    "budget_range": "45k_60k",
                    "timeline": "within_3_months",
                    "current_vehicle": "2016 Toyota Prius",
                },
                "sales_stage": "evaluation",
                "current_interest": "2025 Ion Hybrid",
            },
            "interactions": [
                {
                    "interaction_type": "spec_review",
                    "date": (now - dt.timedelta(days=10)).isoformat(),
                    "duration_minutes": 50,
                    "products_discussed": ["2025 Ion Hybrid"],
                    "customer_feedback": {
                        "interest_level": "medium",
                        "primary_concerns": ["battery_life", "maintenance_cost"],
                        "positive_responses": ["safety_ratings"],
                    },
                    "salesperson_notes": "Requested detailed maintenance schedule and warranty comparison.",
                    "outcome": "researching",
                    "follow_up": {
                        "required": False,
                        "type": "self_service",
                        "date": (now + dt.timedelta(days=14)).isoformat(),
                    },
                    "sales_stage": "evaluation",
                }
            ],
        },
    ]


def seed_customers(samples: Iterable[dict[str, Any]] | None = None) -> None:
    """Persist sample customer profiles and interactions."""
    timestamp = dt.datetime.now(tz=dt.timezone.utc)
    payloads: Sequence[dict[str, Any]] = list(samples) if samples is not None else _default_samples(timestamp)

    session = SessionLocal()
    try:
        profile_repository = CustomerProfileRepository(session=session)
        interaction_repository = InteractionRepository(session=session, profile_repository=profile_repository)
        personality_engine = PersonalityEngine()
        decision_service = DecisionService()

        created = 0
        for entry in payloads:
            profile_payload = dict(entry.get("profile", {}))
            interaction_payloads = list(entry.get("interactions", []))

            profile = profile_repository.create_profile(profile_payload)

            for interaction_payload in interaction_payloads:
                interaction_repository.record(profile.customer_id, interaction_payload)

            stored_profile = profile_repository.get_profile(profile.customer_id)
            evaluation_payload = profile_to_evaluation_payload(stored_profile)
            history = [asdict(record) for record in interaction_repository.list_for_customer(profile.customer_id)]
            personality = personality_engine.evaluate(evaluation_payload)
            decision = decision_service.evaluate(evaluation_payload, interactions=history)
            summary = build_profile_summary(personality, decision)

            profile_repository.record_summary(
                profile.customer_id,
                traits=dict(personality.traits),
                summary=summary,
                recommendation_ready=stored_profile.recommendation_ready,
                profile_score=stored_profile.profile_score,
            )

            created += 1

        print(f"Seeded {created} customer profiles with interactions.")
    finally:
        session.close()


if __name__ == "__main__":
    seed_customers()
