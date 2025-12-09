"""Research Service - Wraps the existing ResearchEngine for FastAPI."""
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for importing api module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.research_engine import ResearchEngine
from api.base_researcher import ResearchResult


class ResearchService:
    """
    Service wrapper around the ResearchEngine for async FastAPI integration.
    """

    def __init__(self):
        self.engine = ResearchEngine()
        self.engine.setup_researchers()
        self._executor = ThreadPoolExecutor(max_workers=4)

    def get_available_providers(self) -> Dict[str, bool]:
        """Get which providers are available (have valid API keys)."""
        return {
            provider: provider in self.engine.researchers
            for provider in ["xai", "google", "openai", "anthropic", "perplexity"]
        }

    async def run_research_async(
        self,
        company: str,
        prompt_id: str,
        mode: str = "basic",
        providers: List[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, ResearchResult]:
        """
        Run research asynchronously.

        Args:
            company: Company name to research
            prompt_id: Prompt ID/name
            mode: "basic" or "deep"
            providers: List of providers to use
            progress_callback: Optional callback for progress updates

        Returns:
            Dict mapping provider name to ResearchResult
        """
        loop = asyncio.get_event_loop()

        # Filter providers to only available ones
        available = self.get_available_providers()
        if providers:
            providers = [p for p in providers if available.get(p, False)]
        else:
            providers = [p for p, ok in available.items() if ok]

        if not providers:
            raise ValueError("No valid providers available")

        # Run in thread pool to avoid blocking
        results = await loop.run_in_executor(
            self._executor,
            lambda: self.engine.run_research(company, prompt_id, mode, providers)
        )

        return results

    async def run_research_with_prompt_async(
        self,
        company: str,
        prompt_content: str,
        mode: str = "basic",
        providers: List[str] = None,
    ) -> Dict[str, ResearchResult]:
        """
        Run research asynchronously with direct prompt content.

        Args:
            company: Company name to research
            prompt_content: The actual prompt text to use
            mode: "basic" or "deep"
            providers: List of providers to use

        Returns:
            Dict mapping provider name to ResearchResult
        """
        loop = asyncio.get_event_loop()

        # Filter providers to only available ones
        available = self.get_available_providers()
        if providers:
            providers = [p for p in providers if available.get(p, False)]
        else:
            providers = [p for p, ok in available.items() if ok]

        if not providers:
            raise ValueError("No valid providers available")

        # Run in thread pool to avoid blocking
        results = await loop.run_in_executor(
            self._executor,
            lambda: self.engine.run_research_with_prompt(company, prompt_content, mode, providers)
        )

        return results

    def save_results(
        self,
        results: Dict[str, ResearchResult],
        company: str,
        prompt_name: str,
    ) -> Dict:
        """
        Save research results to disk.

        Returns:
            Dict with saved_files list, timestamp, and output_dir
        """
        saved_files, timestamp_str = self.engine.save_results(
            results, company, prompt_name
        )
        return {
            "saved_files": saved_files,
            "timestamp": timestamp_str,
            "output_dir": str(self.engine.reports_dir / company / timestamp_str)
        }


# Global instance
_research_service: Optional[ResearchService] = None


def get_research_service() -> ResearchService:
    """Get or create the global research service instance."""
    global _research_service
    if _research_service is None:
        _research_service = ResearchService()
    return _research_service
