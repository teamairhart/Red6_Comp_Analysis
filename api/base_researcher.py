"""
Base class for all LLM research providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ResearchResult:
    """Standardized result from any research provider."""
    provider: str
    model: str
    mode: str  # "basic" or "deep"
    text: str
    citations: List[dict]
    timestamp: datetime
    usage: Optional[dict] = None
    error: Optional[str] = None

    def to_markdown(self) -> str:
        """Convert result to markdown format."""
        md = f"# Research Report - {self.provider.upper()}\n\n"
        md += f"**Model:** {self.model}\n"
        md += f"**Mode:** {self.mode}\n"
        md += f"**Generated:** {self.timestamp.isoformat()}\n\n"
        md += "---\n\n"
        md += self.text

        if self.citations:
            md += "\n\n---\n\n## Sources\n\n"
            for i, citation in enumerate(self.citations, 1):
                url = citation.get('url', citation.get('source', 'N/A'))
                title = citation.get('title', f'Source {i}')
                md += f"{i}. [{title}]({url})\n"

        return md


class BaseResearcher(ABC):
    """Abstract base class for research providers."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.provider_name = "base"

    @abstractmethod
    def basic_research(self, prompt: str, company: str) -> ResearchResult:
        """Run basic (non-deep) research query."""
        pass

    @abstractmethod
    def deep_research(self, prompt: str, company: str) -> ResearchResult:
        """Run deep research query with web search."""
        pass

    def research(self, prompt: str, company: str, mode: str = "basic") -> ResearchResult:
        """
        Run research with specified mode.

        Args:
            prompt: The research prompt template
            company: Company name to research
            mode: "basic" or "deep"

        Returns:
            ResearchResult with standardized format
        """
        # Inject company name into prompt
        full_prompt = prompt.replace("[COMPANY NAME]", company)
        full_prompt = full_prompt.replace("[COMPANY]", company)

        if mode == "deep":
            return self.deep_research(full_prompt, company)
        else:
            return self.basic_research(full_prompt, company)

    def _create_error_result(self, error_msg: str, mode: str) -> ResearchResult:
        """Create a standardized error result."""
        return ResearchResult(
            provider=self.provider_name,
            model="N/A",
            mode=mode,
            text="",
            citations=[],
            timestamp=datetime.utcnow(),
            error=error_msg
        )
