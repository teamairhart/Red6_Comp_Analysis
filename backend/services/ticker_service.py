"""
News Ticker Service

Fetches and curates competitive intelligence news for the ticker display.
Uses OpenAI (or Perplexity) for news gathering and Gemini for relevance scoring.
(Using Gemini during development to utilize trial credits - switch back to Claude for production)
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from dotenv import load_dotenv

# Load .env from project root (parent of backend)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from models.ticker import (
    TickerItem,
    TickerData,
    TickerImportance,
    TickerCategory,
)

logger = logging.getLogger(__name__)

# Data storage path
TICKER_DATA_PATH = Path(__file__).parent.parent / "data" / "ticker.json"

# Primary competitors to monitor
PRIMARY_COMPETITORS = [
    "Elbit Systems",
    "Thales",
    "BAE Systems",
]

# Other competitors to monitor
OTHER_COMPETITORS = [
    "Lockheed Martin",
    "Northrop Grumman",
    "Raytheon",
    "L3Harris",
    "Leonardo",
    "SAAB",
    "Rheinmetall",
]

# Topics relevant to Red 6's competitive intelligence
RELEVANT_TOPICS = [
    "defense contracts",
    "military training systems",
    "simulation technology",
    "augmented reality military",
    "head-mounted displays",
    "pilot training",
    "aviation training",
    "defense technology",
    "government procurement",
    "defense acquisitions",
]


def load_ticker_data() -> TickerData:
    """Load ticker data from storage."""
    if TICKER_DATA_PATH.exists():
        try:
            with open(TICKER_DATA_PATH, "r") as f:
                data = json.load(f)
            return TickerData(**data)
        except Exception as e:
            logger.error(f"Failed to load ticker data: {e}")
    return TickerData()


def save_ticker_data(data: TickerData) -> None:
    """Save ticker data to storage."""
    TICKER_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TICKER_DATA_PATH, "w") as f:
        json.dump(data.model_dump(mode="json"), f, indent=2, default=str)


async def fetch_competitor_news(hours_lookback: int = 48) -> str:
    """
    Fetch recent news about competitors using OpenAI web search (or Perplexity fallback).
    Returns raw news content for analysis.
    """
    from openai import OpenAI

    # Build the search query (used by all providers)
    companies = ", ".join(PRIMARY_COMPETITORS + OTHER_COMPETITORS[:3])

    # Get current date for explicit recency requirements
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")

    query = f"""Find the most recent and significant news from the past 7 DAYS about these defense companies: {companies}.

**DATE CONTEXT**: Today's date is {current_date}.
- Prioritize news from the last few days (November 2025)
- DO NOT include any news from 2024 or earlier years
- DO NOT include annual reports or year-end summaries from previous years
- Accept news from the past week if no very recent news is available

Focus on:
- Contract awards and losses
- Executive changes and leadership moves
- Technology announcements and R&D developments
- Mergers, acquisitions, and partnerships
- Military training and simulation systems
- Augmented reality and head-mounted display technology

For each news item, provide IN THIS EXACT FORMAT:
HEADLINE: [The headline]
SUMMARY: [1-2 sentence summary]
COMPANY: [Company name]
SOURCE: [Publication name]
URL: [Full URL to the original article - THIS IS REQUIRED]
DATE: [Publication date]
SIGNIFICANCE: [Why this matters for competitive intelligence]

---

IMPORTANT REQUIREMENTS:
1. You MUST include the actual source URL for each news item. Do not skip the URL field.
2. Prioritize the MOST RECENT news first
3. If you find articles from 2023 or 2024, DO NOT include them
4. Include at least 10-15 items if available

Prioritize news that would be most relevant to a company competing in military training, simulation, and AR/HMD technology."""

    # Try OpenAI first (with web search via Responses API)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and not openai_key.startswith("sk-your"):
        try:
            client = OpenAI(api_key=openai_key)
            logger.info("Using OpenAI for news fetching")

            response = client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=query,
            )

            # Extract text from response (use output_text if available)
            result_text = response.output_text if hasattr(response, 'output_text') else ""
            logger.info(f"OpenAI raw news (first 500 chars): {result_text[:500] if result_text else 'EMPTY'}")

            if result_text:
                return result_text

        except Exception as e:
            logger.warning(f"OpenAI web search failed: {e}, trying Perplexity fallback")

    # Try Perplexity as fallback
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    if perplexity_key and not perplexity_key.startswith("pplx-your"):
        try:
            client = OpenAI(
                api_key=perplexity_key,
                base_url="https://api.perplexity.ai"
            )
            logger.info("Using Perplexity for news fetching")

            response = client.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a competitive intelligence analyst focused on the defense technology sector. Provide factual, well-sourced news summaries."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.3,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.warning(f"Perplexity query failed: {e}")

    # Final fallback to Gemini
    return await _fetch_news_fallback(hours_lookback)


async def _fetch_news_fallback(hours_lookback: int = 48) -> str:
    """
    Fallback news fetching using Google Gemini if Perplexity is unavailable.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("No news API available (PERPLEXITY_API_KEY and GEMINI_API_KEY not set)")
        return ""

    try:
        from google import genai

        client = genai.Client(api_key=gemini_key)

        companies = ", ".join(PRIMARY_COMPETITORS + OTHER_COMPETITORS[:3])

        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")

        query = f"""Search for the most recent news (past 7 days) about these defense companies: {companies}.

**DATE CONTEXT**: Today is {current_date}. Prioritize news from November 2025.
- DO NOT include any news from 2024 or earlier
- DO NOT include annual reports or year-end summaries from previous years
- Accept news from the past week

Focus on contract awards, executive changes, technology announcements, M&A activity, and military training/simulation developments.

For each item found, provide the headline, summary, company, source with URL, publication date, and why it's significant for competitive intelligence."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=query,
            config={
                "tools": [{"google_search": {}}],
            }
        )

        return response.text

    except Exception as e:
        logger.error(f"Gemini fallback failed: {e}")
        return ""


async def analyze_and_rank_news(raw_news: str, max_items: int = 15) -> List[TickerItem]:
    """
    Use Gemini to analyze raw news and create ranked ticker items.
    (Switched from Claude to use Gemini trial credits during development)
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("GEMINI_API_KEY not set, cannot analyze news")
        return []

    if not raw_news or len(raw_news.strip()) < 100:
        logger.warning("No substantial news content to analyze")
        return []

    from google import genai
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")

    client = genai.Client(api_key=gemini_key)

    analysis_prompt = f"""You are a competitive intelligence analyst for Red 6, a company that develops augmented reality (AR) training systems and head-mounted displays (HMDs) for military pilot training.

**DATE CONTEXT**: Today's date is {current_date}.
- Prioritize news from the past week (November 2025)
- REJECT any news from 2024 or earlier
- REJECT articles about "2023 reports", "2024 year-end", or similar retrospective content

Analyze the following news about defense industry competitors and create a prioritized list of the {max_items} most relevant items for Red 6's competitive intelligence.

For each item, assess:
1. **Relevance to Red 6**: How directly does this affect Red 6's competitive position?
   - Training systems, simulation, AR/HMD, pilot training = HIGH relevance
   - Defense contracts, military technology = MEDIUM relevance
   - General corporate news = LOW relevance

2. **Importance Level**:
   - critical: Direct competitive threat, contract in Red 6's space, major competitor win/loss
   - notable: Significant development worth monitoring
   - routine: Background information, general news

3. **Category**: contract, executive, technology, acquisition, partnership, financial, product, general

RAW NEWS TO ANALYZE:
{raw_news}

Respond with a JSON array of ticker items. Each item should have:
- "headline": Concise headline (max 80 chars)
- "summary": 1-2 sentence summary
- "company": Primary company mentioned
- "category": One of: contract, executive, technology, acquisition, partnership, financial, product, general
- "importance": One of: critical, notable, routine (USE LOWERCASE!)
- "source_name": News source if mentioned (e.g., "Defense News", "Reuters")
- "source_url": The URL from the raw news if present - extract the actual URL (e.g., "https://...") and include it
- "relevance_reason": Brief explanation of why this matters to Red 6 (max 100 chars)

CRITICAL REQUIREMENTS:
1. Extract and include the source_url for each item when available
2. DO NOT include ANY news from 2023 or 2024 - only November 2025 news
3. Use LOWERCASE for importance values: "critical", "notable", "routine"

Sort by importance (critical first) then by relevance to Red 6's core business.

Return ONLY the JSON array, no other text."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=analysis_prompt,
        )

        # Parse the response
        response_text = response.text.strip()
        logger.info(f"Gemini raw response (first 500 chars): {response_text[:500]}")

        # Handle markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        items_data = json.loads(response_text)
        logger.info(f"Parsed {len(items_data)} items from Gemini response")

        # Convert to TickerItem objects
        ticker_items = []
        for i, item in enumerate(items_data[:max_items]):
            try:
                # Normalize importance and category to lowercase (Gemini may return UPPERCASE)
                importance_val = item.get("importance", "routine").lower()
                category_val = item.get("category", "general").lower()

                ticker_item = TickerItem(
                    id=str(uuid.uuid4()),
                    headline=item.get("headline", "Unknown headline")[:100],
                    summary=item.get("summary", "")[:300],
                    company=item.get("company", "Unknown"),
                    category=TickerCategory(category_val),
                    importance=TickerImportance(importance_val),
                    source_name=item.get("source_name"),
                    source_url=item.get("source_url"),
                    relevance_reason=item.get("relevance_reason", "")[:150],
                    created_at=datetime.utcnow(),
                )
                ticker_items.append(ticker_item)
            except Exception as e:
                logger.warning(f"Failed to parse ticker item {i}: {e}")
                continue

        return ticker_items

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return []


async def refresh_ticker(
    force: bool = False,
    hours_lookback: int = 48,
    max_items: int = 15
) -> TickerData:
    """
    Refresh the ticker data if stale or forced.

    Args:
        force: Force refresh even if data is not stale
        hours_lookback: How many hours back to look for news
        max_items: Maximum number of items to return

    Returns:
        Updated TickerData
    """
    current_data = load_ticker_data()

    # Check if refresh is needed
    if not force and not current_data.is_stale() and len(current_data.items) > 0:
        logger.info("Ticker data is fresh, skipping refresh")
        return current_data

    logger.info(f"Refreshing ticker data (force={force}, lookback={hours_lookback}h)")

    # Fetch news
    raw_news = await fetch_competitor_news(hours_lookback)

    if not raw_news:
        logger.warning("No news fetched, keeping existing data")
        return current_data

    # Analyze and rank
    items = await analyze_and_rank_news(raw_news, max_items)

    if not items:
        logger.warning("No items extracted from news, keeping existing data")
        return current_data

    # Create new ticker data
    new_data = TickerData(
        items=items,
        last_updated=datetime.utcnow(),
        query_timestamp=datetime.utcnow(),
        stale_after_hours=4,
    )

    # Save to storage
    save_ticker_data(new_data)

    logger.info(f"Ticker refreshed with {len(items)} items")
    return new_data


def get_ticker_data() -> TickerData:
    """Get current ticker data (sync version for simple retrieval)."""
    return load_ticker_data()
