"""Ticker API Router - Competitive Intelligence News Feed"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

from models.ticker import TickerData, TickerRefreshRequest
from services.ticker_service import (
    get_ticker_data,
    refresh_ticker,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ticker", tags=["ticker"])


@router.get("", response_model=TickerData)
async def get_ticker():
    """
    Get current ticker data.

    Returns cached ticker items if available and not stale.
    If data is stale or empty, returns what's available (may be empty).
    Use POST /api/ticker/refresh to fetch fresh data.
    """
    data = get_ticker_data()
    return data


@router.get("/status")
async def get_ticker_status():
    """
    Get ticker status information.

    Returns information about when the ticker was last updated
    and whether a refresh is needed.
    """
    data = get_ticker_data()
    return {
        "item_count": len(data.items),
        "last_updated": data.last_updated.isoformat() if data.last_updated else None,
        "is_stale": data.is_stale(),
        "stale_after_hours": data.stale_after_hours,
    }


@router.post("/refresh", response_model=TickerData)
async def refresh_ticker_data(request: TickerRefreshRequest = TickerRefreshRequest()):
    """
    Refresh ticker data by fetching latest news.

    This endpoint:
    1. Queries Perplexity for recent competitor news
    2. Uses Claude to analyze and rank by relevance to Red 6
    3. Saves and returns the refreshed ticker data

    Args:
        force: Force refresh even if data is not stale
        hours_lookback: How many hours back to search (default 48)
        max_items: Maximum items to return (default 15)

    Note: This can take 10-30 seconds depending on API response times.
    """
    try:
        data = await refresh_ticker(
            force=request.force,
            hours_lookback=request.hours_lookback,
            max_items=request.max_items,
        )
        return data
    except Exception as e:
        logger.error(f"Ticker refresh failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh ticker: {str(e)}"
        )


@router.post("/refresh-async")
async def refresh_ticker_async(
    background_tasks: BackgroundTasks,
    request: TickerRefreshRequest = TickerRefreshRequest()
):
    """
    Start an async ticker refresh in the background.

    Returns immediately while the refresh happens in the background.
    Use GET /api/ticker/status to check when refresh completes.
    """
    async def do_refresh():
        try:
            await refresh_ticker(
                force=request.force,
                hours_lookback=request.hours_lookback,
                max_items=request.max_items,
            )
            logger.info("Background ticker refresh completed")
        except Exception as e:
            logger.error(f"Background ticker refresh failed: {e}")

    background_tasks.add_task(do_refresh)

    return {
        "status": "refresh_started",
        "message": "Ticker refresh started in background. Check /api/ticker/status for completion."
    }
