"""
News Ticker Models

Data models for the competitive intelligence news ticker.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TickerImportance(str, Enum):
    """Importance level for ticker items."""
    CRITICAL = "critical"    # Direct competitive threat, major contract loss/win
    NOTABLE = "notable"      # Significant development worth watching
    ROUTINE = "routine"      # General news, background information


class TickerCategory(str, Enum):
    """Category of ticker item."""
    CONTRACT = "contract"           # Contract awards, losses, bids
    EXECUTIVE = "executive"         # Leadership changes
    TECHNOLOGY = "technology"       # New tech, R&D announcements
    ACQUISITION = "acquisition"     # M&A activity
    PARTNERSHIP = "partnership"     # New partnerships, JVs
    FINANCIAL = "financial"         # Earnings, funding, financial news
    PRODUCT = "product"             # Product launches, updates
    GENERAL = "general"             # Other news


class TickerItem(BaseModel):
    """A single news ticker item."""
    id: str
    headline: str
    summary: str                    # 1-2 sentence summary
    company: str                    # Primary company mentioned
    category: TickerCategory
    importance: TickerImportance
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    published_at: Optional[datetime] = None
    relevance_reason: str           # Why this matters to Red 6
    created_at: datetime = datetime.utcnow()


class TickerData(BaseModel):
    """Container for ticker data with metadata."""
    items: List[TickerItem] = []
    last_updated: datetime = datetime.utcnow()
    query_timestamp: datetime = datetime.utcnow()
    stale_after_hours: int = 4      # Consider data stale after this many hours

    def is_stale(self) -> bool:
        """Check if the ticker data is stale and needs refresh."""
        from datetime import timedelta
        age = datetime.utcnow() - self.last_updated
        return age > timedelta(hours=self.stale_after_hours)


class TickerRefreshRequest(BaseModel):
    """Request to refresh ticker data."""
    force: bool = False             # Force refresh even if not stale
    hours_lookback: int = 48        # How far back to look for news
    max_items: int = 15             # Maximum items to return
