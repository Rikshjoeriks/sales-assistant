"""Objection handling generator (T055).

Builds on PromptBuilder to tailor a prompt focused on handling customer
objections informed by context.decision.objection_themes and concerns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.app.recommendations.clients.chatgpt_client import ChatGPTClient
from src.app.recommendations.services.context_builder import RecommendationContext
from src.app.recommendations.services.prompt_builder import PromptBuilder
from src.app.recommendations.services.retrieval_service import RetrievalBundle


@dataclass(slots=True)
class ObjectionService:
    prompt_builder: PromptBuilder
    chat_client: ChatGPTClient

    async def generate(
        self,
        *,
        context: RecommendationContext,
        retrieval: RetrievalBundle,
        temperature: float = 0.4,
        prompt_token_budget: int = 800,
        timeout: float | None = None,
    ) -> str:
        # Start from the base prompt
        parts = self.prompt_builder.build(
            context=context,
            retrieval=retrieval,
            tone="reassuring",
            output_format="objection_plan",
            prompt_token_budget=prompt_token_budget,
        )

        # Augment with explicit objection handling instructions
        objections = context.decision.objection_themes if context.decision else []
        concerns = context.context.customer_concerns if context.context else []
        augmentation = (
            "Address the customer's likely objections and concerns explicitly.\n"
            f"Objection themes: {', '.join(objections) if objections else 'none'}.\n"
            f"Customer concerns: {', '.join(concerns) if concerns else 'none'}.\n"
            "Provide empathetic, concise responses with evidence and citations."
        )
        parts.messages.append({"role": "user", "content": augmentation})

        # Generate objection handling plan
        text = await self.chat_client.chat(messages=parts.messages, temperature=temperature, timeout=timeout)
        return text


__all__ = ["ObjectionService"]
