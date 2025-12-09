"""API Routers"""
from .prompts import router as prompts_router
from .research import router as research_router
from .reports import router as reports_router
from .sources import router as sources_router
from .delta import router as delta_router
from .schedule import router as schedule_router
from .ticker import router as ticker_router

__all__ = [
    "prompts_router",
    "research_router",
    "reports_router",
    "sources_router",
    "delta_router",
    "schedule_router",
    "ticker_router",
]
