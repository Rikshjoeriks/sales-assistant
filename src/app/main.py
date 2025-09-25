"""Entry point for the Sales Assistant API."""
from fastapi import FastAPI

from src.app.core.config import settings
from src.app.core.observability import configure_observability
from src.app.knowledge.api.router import router as knowledge_router

app = FastAPI(
    title="Sales Assistant API",
    version="0.1.0",
    description=(
        "Domain-specific sales assistant that combines knowledge ingestion, customer intelligence, "
        "and personalized recommendations."
    ),
)

configure_observability(app)

app.include_router(knowledge_router)


@app.get("/health", tags=["Health"], summary="API health probe")
async def health_check() -> dict[str, str]:
    """Lightweight readiness probe for orchestration systems."""
    return {
        "status": "ok",
        "environment": settings.environment,
        "service": "sales-assistant-api",
    }
