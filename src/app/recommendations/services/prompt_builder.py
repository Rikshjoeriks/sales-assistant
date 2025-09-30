"""Prompt template manager for recommendation synthesis (T052).

Builds structured prompt parts from RecommendationContext and RetrievalBundle.
Provides a token-budget-aware truncation of retrieved evidence.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.app.recommendations.services.context_builder import RecommendationContext
from src.app.recommendations.services.retrieval_service import RetrievalBundle


@dataclass(slots=True)
class PromptParts:
    system: str
    user: str
    messages: list[dict[str, str]]


class PromptBuilder:
    """Assemble chat prompt parts with light heuristics.

    Contract:
    - Inputs: context, retrieval, optional tone/output_format/token budget
    - Output: PromptParts with `system`, `user`, and `messages` [system, user]
    - Truncation: naive item-count truncation derived from token budget
    """

    def build(
        self,
        *,
        context: RecommendationContext,
        retrieval: RetrievalBundle,
        tone: str = "consultative",
        output_format: str = "bullet_points",
        prompt_token_budget: int = 800,
    ) -> PromptParts:
        system = self._build_system_message(tone)
        user = self._build_user_message(context, retrieval, output_format, prompt_token_budget)
        return PromptParts(system=system, user=user, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])

    # ------------------------------------------------------------------
    # Builders
    # ------------------------------------------------------------------
    def _build_system_message(self, tone: str) -> str:
        return (
            "You are a helpful sales assistant. Provide actionable, courteous, and accurate recommendations. "
            f"Adopt a {tone} tone and cite sources when relevant."
        )

    def _build_user_message(
        self,
        context: RecommendationContext,
        retrieval: RetrievalBundle,
        output_format: str,
        prompt_token_budget: int,
    ) -> str:
        c = context.context
        p = context.personality
        d = context.decision

        # Decide how many items to include based on a simple budget heuristic.
        # Rough heuristic: keep ~40 tokens for framing + ~80 per item.
        max_items = max(1, min(len(retrieval.items), (prompt_token_budget - 40) // 80))
        items = retrieval.items[:max_items]

        evidence_lines: list[str] = []
        for idx, item in enumerate(items, start=1):
            title = item.concept.title
            source_title = item.source.title
            snippet = item.concept.content[:220].replace("\n", " ")
            evidence_lines.append(f"{idx}. {title} — {snippet} (source: {source_title})")

        concerns = ", ".join(c.customer_concerns) if c.customer_concerns else "none"
        competitors = ", ".join(c.competitive_alternatives) if c.competitive_alternatives else "none"
        principles = ", ".join(d.primary_factors + d.secondary_factors)

        user = (
            f"Customer is interested in {c.product_interest}. Sales stage: {c.sales_stage}.\n"
            f"personality: {p.type} (style: {p.communication_style or 'unknown'}; primary={p.primary_trait}).\n"
            f"Decision drivers: {principles or 'n/a'}. Urgency: {d.urgency_level or 'low'}.\n"
            f"Primary concerns: {concerns}. Competitive alternatives: {competitors}.\n"
            f"Context: {c.context_description}.\n\n"
            f"Use the following evidence to craft {output_format} recommendations with citations:\n"
            + "\n".join(evidence_lines)
        )

        return user


__all__ = ["PromptParts", "PromptBuilder"]
