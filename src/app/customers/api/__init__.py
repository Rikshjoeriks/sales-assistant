"""Customer API router exports."""

from src.app.customers.api.analytics_router import router as customer_analytics_router
from src.app.customers.api.router import router as customers_router

__all__ = ["customers_router", "customer_analytics_router"]
