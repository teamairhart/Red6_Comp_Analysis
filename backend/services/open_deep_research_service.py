"""
Open Deep Research Integration Service

Integrates with the LangChain Open Deep Research server running at localhost:2024
to provide high-quality, multi-agent deep research capabilities.

This service enables:
- Running deep research using different LLM providers (OpenAI, Anthropic, Google, etc.)
- Web search integration via Tavily
- Multi-step research workflow (clarification → research → compression → synthesis)
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Use langgraph SDK for interacting with the LangGraph server
from langgraph_sdk import get_client

logger = logging.getLogger(__name__)

# Open Deep Research server URL
OPEN_DEEP_RESEARCH_URL = os.getenv("OPEN_DEEP_RESEARCH_URL", "http://127.0.0.1:2024")

# Default timeout for deep research (in seconds) - configurable via environment
# Deep research can take 3-15 minutes depending on query complexity
DEFAULT_DEEP_RESEARCH_TIMEOUT = int(os.getenv("DEEP_RESEARCH_TIMEOUT_SECONDS", "900"))  # 15 minutes default

# Model mappings for each provider
# Maps our provider IDs to Open Deep Research model format (provider:model)
PROVIDER_MODEL_MAPPING = {
    "openai": {
        "research_model": "openai:gpt-4.1",
        "compression_model": "openai:gpt-4.1-mini",
        "final_report_model": "openai:gpt-4.1",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",  # Tavily works well with all models
    },
    "anthropic": {
        "research_model": "anthropic:claude-sonnet-4-20250514",
        "compression_model": "anthropic:claude-sonnet-4-20250514",
        "final_report_model": "anthropic:claude-sonnet-4-20250514",
        "summarization_model": "openai:gpt-4.1-mini",  # Use OpenAI for summarization (faster)
        "search_api": "tavily",  # Can also use "anthropic" for native search
    },
    "google": {
        "research_model": "google_genai:gemini-2.0-flash",
        "compression_model": "google_genai:gemini-2.0-flash",
        "final_report_model": "google_genai:gemini-2.0-flash",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
    },
    "xai": {
        # xAI/Grok models - using OpenAI compatible format
        "research_model": "openai:grok-3-mini",  # xAI uses OpenAI-compatible API
        "compression_model": "openai:gpt-4.1-mini",
        "final_report_model": "openai:grok-3-mini",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
    },
    "perplexity": {
        # Perplexity has its own search, but we'll use standard models with Tavily
        "research_model": "openai:gpt-4.1",  # Perplexity API not directly supported
        "compression_model": "openai:gpt-4.1-mini",
        "final_report_model": "openai:gpt-4.1",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
    },
}

# Alternative high-quality model configs for "deep" mode
DEEP_MODE_MODEL_MAPPING = {
    "openai": {
        "research_model": "openai:gpt-4.1",
        "compression_model": "openai:gpt-4.1",
        "final_report_model": "openai:gpt-4.1",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
        "max_researcher_iterations": 6,
        "max_react_tool_calls": 15,
    },
    "anthropic": {
        "research_model": "anthropic:claude-sonnet-4-20250514",
        "compression_model": "anthropic:claude-sonnet-4-20250514",
        "final_report_model": "anthropic:claude-sonnet-4-20250514",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
        "max_researcher_iterations": 6,
        "max_react_tool_calls": 15,
    },
    "google": {
        "research_model": "google_genai:gemini-2.0-flash",
        "compression_model": "google_genai:gemini-2.0-flash",
        "final_report_model": "google_genai:gemini-2.0-flash",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
        "max_researcher_iterations": 6,
        "max_react_tool_calls": 15,
    },
    "xai": {
        "research_model": "openai:gpt-4.1",  # Fallback to GPT-4.1 for best results
        "compression_model": "openai:gpt-4.1-mini",
        "final_report_model": "openai:gpt-4.1",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
        "max_researcher_iterations": 6,
        "max_react_tool_calls": 15,
    },
    "perplexity": {
        "research_model": "openai:gpt-4.1",
        "compression_model": "openai:gpt-4.1-mini",
        "final_report_model": "openai:gpt-4.1",
        "summarization_model": "openai:gpt-4.1-mini",
        "search_api": "tavily",
        "max_researcher_iterations": 6,
        "max_react_tool_calls": 15,
    },
}


@dataclass
class DeepResearchResult:
    """Result from an Open Deep Research run."""
    provider: str
    model: str
    content: str
    research_brief: Optional[str] = None
    status: str = "completed"
    error: Optional[str] = None
    citations: List[Dict[str, str]] = None
    raw_notes: Optional[str] = None
    duration_seconds: float = 0.0

    def __post_init__(self):
        if self.citations is None:
            self.citations = []


class OpenDeepResearchService:
    """
    Service for running deep research via the Open Deep Research LangGraph server.

    This service wraps the LangGraph SDK client and provides a simple interface
    for running research with different LLM providers.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize the Open Deep Research service.

        Args:
            base_url: URL of the Open Deep Research server (default: localhost:2024)
        """
        self.base_url = base_url or OPEN_DEEP_RESEARCH_URL
        self._client = None
        self._graph_id = "Deep Researcher"  # Default graph ID from langgraph.json

    @property
    def client(self):
        """Lazy initialization of the LangGraph SDK client."""
        if self._client is None:
            self._client = get_client(url=self.base_url)
        return self._client

    async def check_health(self) -> bool:
        """Check if the Open Deep Research server is healthy."""
        try:
            # Try to list assistants to verify connection
            assistants = await self.client.assistants.search(limit=1)
            return True
        except Exception as e:
            logger.error(f"Open Deep Research server health check failed: {e}")
            return False

    def get_model_config(self, provider: str, deep_mode: bool = True) -> Dict[str, Any]:
        """
        Get the model configuration for a specific provider.

        Args:
            provider: Provider ID (openai, anthropic, google, xai, perplexity)
            deep_mode: Whether to use deep mode config (more iterations)

        Returns:
            Configuration dictionary for Open Deep Research
        """
        mapping = DEEP_MODE_MODEL_MAPPING if deep_mode else PROVIDER_MODEL_MAPPING

        if provider not in mapping:
            logger.warning(f"Unknown provider {provider}, falling back to OpenAI")
            provider = "openai"

        config = mapping[provider].copy()

        # Add common settings
        config.update({
            "allow_clarification": False,  # Skip clarification for automated use
            "max_concurrent_research_units": 3,  # Balance speed vs rate limits
        })

        return config

    async def run_research(
        self,
        query: str,
        provider: str = "openai",
        company: Optional[str] = None,
        deep_mode: bool = True,
        timeout_seconds: int = None,  # Uses DEFAULT_DEEP_RESEARCH_TIMEOUT if not specified
    ) -> DeepResearchResult:
        """
        Run a deep research query using the specified provider.

        Args:
            query: The research query/prompt
            provider: LLM provider to use (openai, anthropic, google, xai, perplexity)
            company: Optional company name for competitive intelligence
            deep_mode: Whether to use deep mode settings
            timeout_seconds: Maximum time to wait for research completion

        Returns:
            DeepResearchResult with the research output
        """
        start_time = datetime.utcnow()

        # Use default timeout if not specified
        if timeout_seconds is None:
            timeout_seconds = DEFAULT_DEEP_RESEARCH_TIMEOUT

        try:
            # Get model configuration for this provider
            config = self.get_model_config(provider, deep_mode)

            # Build the research message
            if company:
                research_message = f"""Conduct comprehensive competitive intelligence research on {company}.

Research Focus:
{query}

Please provide:
1. Current factual information with dates and sources
2. Specific numbers, financial data, and metrics where available
3. Recent developments (within the past 6-12 months)
4. Strategic analysis and competitive implications
5. Areas of uncertainty or conflicting information

Be thorough and cite your sources."""
            else:
                research_message = query

            logger.info(f"Starting Open Deep Research for provider {provider}")
            logger.debug(f"Config: {config}")

            # Create a thread for this research run
            thread = await self.client.threads.create()
            logger.debug(f"Created thread: {thread['thread_id']}")

            # Start the research run
            run = await self.client.runs.create(
                thread_id=thread["thread_id"],
                assistant_id=self._graph_id,
                input={"messages": [{"role": "user", "content": research_message}]},
                config={"configurable": config},
            )

            logger.debug(f"Started run: {run['run_id']}")

            # Wait for completion with polling
            final_state = await self._wait_for_completion(
                thread["thread_id"],
                run["run_id"],
                timeout_seconds
            )

            # Extract results from final state
            duration = (datetime.utcnow() - start_time).total_seconds()

            if final_state is None:
                return DeepResearchResult(
                    provider=provider,
                    model=config.get("research_model", "unknown"),
                    content="",
                    status="failed",
                    error="Research timed out or failed to complete",
                    duration_seconds=duration,
                )

            # Extract the final report from the state
            final_report = final_state.get("final_report", "")
            research_brief = final_state.get("research_brief", "")
            notes = final_state.get("notes", [])
            raw_notes = final_state.get("raw_notes", [])

            # Also check messages for the final response
            messages = final_state.get("messages", [])
            if not final_report and messages:
                # Get content from last AI message
                for msg in reversed(messages):
                    if isinstance(msg, dict) and msg.get("type") == "ai":
                        final_report = msg.get("content", "")
                        break
                    elif hasattr(msg, "content") and hasattr(msg, "type") and msg.type == "ai":
                        final_report = msg.content
                        break

            return DeepResearchResult(
                provider=provider,
                model=config.get("research_model", "unknown"),
                content=final_report,
                research_brief=research_brief,
                status="completed",
                raw_notes="\n".join(raw_notes) if raw_notes else None,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Open Deep Research failed for provider {provider}: {e}")
            import traceback
            logger.error(traceback.format_exc())

            return DeepResearchResult(
                provider=provider,
                model=DEEP_MODE_MODEL_MAPPING.get(provider, {}).get("research_model", "unknown"),
                content="",
                status="failed",
                error=str(e),
                duration_seconds=duration,
            )

    async def _wait_for_completion(
        self,
        thread_id: str,
        run_id: str,
        timeout_seconds: int
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a research run to complete.

        Args:
            thread_id: The thread ID
            run_id: The run ID
            timeout_seconds: Maximum time to wait

        Returns:
            Final state dictionary or None if failed/timed out
        """
        start_time = datetime.utcnow()
        poll_interval = 2.0  # seconds

        while True:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                logger.warning(f"Research run {run_id} timed out after {timeout_seconds}s")
                return None

            try:
                # Check run status
                run = await self.client.runs.get(thread_id=thread_id, run_id=run_id)
                status = run.get("status", "unknown")

                logger.debug(f"Run {run_id} status: {status} (elapsed: {elapsed:.1f}s)")

                if status == "success":
                    # Get the final state
                    state = await self.client.threads.get_state(thread_id=thread_id)
                    return state.get("values", {})

                elif status in ["error", "failed"]:
                    logger.error(f"Research run {run_id} failed with status: {status}")
                    return None

                elif status in ["pending", "running"]:
                    # Still running, wait and poll again
                    await asyncio.sleep(poll_interval)
                    continue

                else:
                    logger.warning(f"Unknown run status: {status}")
                    await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error polling run status: {e}")
                await asyncio.sleep(poll_interval)

    async def run_research_parallel(
        self,
        query: str,
        providers: List[str],
        company: Optional[str] = None,
        deep_mode: bool = True,
        timeout_seconds: int = None,  # Uses DEFAULT_DEEP_RESEARCH_TIMEOUT if not specified
    ) -> Dict[str, DeepResearchResult]:
        """
        Run deep research in parallel across multiple providers.

        Args:
            query: The research query/prompt
            providers: List of provider IDs to use
            company: Optional company name for competitive intelligence
            deep_mode: Whether to use deep mode settings
            timeout_seconds: Maximum time per provider

        Returns:
            Dictionary mapping provider ID to DeepResearchResult
        """
        logger.info(f"Starting parallel deep research with providers: {providers}")

        # Create tasks for each provider
        tasks = [
            self.run_research(
                query=query,
                provider=provider,
                company=company,
                deep_mode=deep_mode,
                timeout_seconds=timeout_seconds,
            )
            for provider in providers
        ]

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dictionary
        results_dict = {}
        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                results_dict[provider] = DeepResearchResult(
                    provider=provider,
                    model="unknown",
                    content="",
                    status="failed",
                    error=str(result),
                )
            else:
                results_dict[provider] = result

        return results_dict


# Global service instance
_service: Optional[OpenDeepResearchService] = None


def get_open_deep_research_service() -> OpenDeepResearchService:
    """Get or create the global Open Deep Research service instance."""
    global _service
    if _service is None:
        _service = OpenDeepResearchService()
    return _service


async def run_open_deep_research(
    query: str,
    providers: List[str],
    company: Optional[str] = None,
    deep_mode: bool = True,
) -> Dict[str, DeepResearchResult]:
    """
    Convenience function to run Open Deep Research.

    Args:
        query: The research query/prompt
        providers: List of provider IDs to use
        company: Optional company name
        deep_mode: Whether to use deep mode

    Returns:
        Dictionary mapping provider ID to DeepResearchResult
    """
    service = get_open_deep_research_service()
    return await service.run_research_parallel(
        query=query,
        providers=providers,
        company=company,
        deep_mode=deep_mode,
    )
