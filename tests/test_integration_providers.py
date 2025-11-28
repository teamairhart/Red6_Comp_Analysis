"""
Integration tests for LLM providers.

These tests require actual API keys and will make real API calls.
Run with: pytest tests/test_integration_providers.py -m integration

To skip these tests, use: pytest -m "not integration"
"""
import pytest
import os
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


def has_api_key(key_name: str) -> bool:
    """Check if an API key is configured and not a placeholder."""
    key = os.getenv(key_name, "")
    if not key:
        return False
    # Check for common placeholder patterns
    placeholders = ["your-", "sk-your", "xai-your", "pplx-your"]
    return not any(p in key.lower() for p in placeholders)


# Skip conditions for each provider
skip_openai = pytest.mark.skipif(
    not has_api_key("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not configured"
)
skip_anthropic = pytest.mark.skipif(
    not has_api_key("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not configured"
)
skip_google = pytest.mark.skipif(
    not has_api_key("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not configured"
)
skip_xai = pytest.mark.skipif(
    not has_api_key("XAI_API_KEY"),
    reason="XAI_API_KEY not configured"
)
skip_perplexity = pytest.mark.skipif(
    not has_api_key("PERPLEXITY_API_KEY"),
    reason="PERPLEXITY_API_KEY not configured"
)


@pytest.mark.integration
@pytest.mark.slow
class TestOpenAIIntegration:
    """Integration tests for OpenAI provider."""

    @skip_openai
    def test_openai_basic_research(self):
        """Test OpenAI basic research returns valid result."""
        from api.openai_research import OpenAIResearcher

        researcher = OpenAIResearcher(os.getenv("OPENAI_API_KEY"))
        result = researcher.basic_research(
            "What is the company's recent stock performance?",
            "Apple Inc"
        )

        assert result.provider == "openai"
        assert result.mode == "basic"
        assert result.text  # Should have some content
        assert result.error is None
        assert result.model is not None

    @skip_openai
    def test_openai_returns_citations(self):
        """Test that OpenAI returns citations from web search."""
        from api.openai_research import OpenAIResearcher

        researcher = OpenAIResearcher(os.getenv("OPENAI_API_KEY"))
        result = researcher.basic_research(
            "What are the latest news headlines about this company?",
            "Microsoft"
        )

        # Web search should return citations
        assert isinstance(result.citations, list)


@pytest.mark.integration
@pytest.mark.slow
class TestAnthropicIntegration:
    """Integration tests for Anthropic provider."""

    @skip_anthropic
    def test_anthropic_basic_research(self):
        """Test Anthropic basic research returns valid result."""
        from api.anthropic_research import AnthropicResearcher

        researcher = AnthropicResearcher(os.getenv("ANTHROPIC_API_KEY"))
        result = researcher.basic_research(
            "What is the company's market position?",
            "Google"
        )

        assert result.provider == "anthropic"
        assert result.mode == "basic"
        assert result.text
        assert result.error is None

    @skip_anthropic
    def test_anthropic_has_usage_data(self):
        """Test that Anthropic returns usage data."""
        from api.anthropic_research import AnthropicResearcher

        researcher = AnthropicResearcher(os.getenv("ANTHROPIC_API_KEY"))
        result = researcher.basic_research(
            "Brief company overview",
            "Amazon"
        )

        assert result.usage is not None


@pytest.mark.integration
@pytest.mark.slow
class TestGoogleIntegration:
    """Integration tests for Google Gemini provider."""

    @skip_google
    def test_google_basic_research(self):
        """Test Google basic research returns valid result."""
        from api.google_research import GoogleResearcher

        researcher = GoogleResearcher(os.getenv("GEMINI_API_KEY"))
        result = researcher.basic_research(
            "What are the company's main products?",
            "Tesla"
        )

        assert result.provider == "google"
        assert result.mode == "basic"
        assert result.text
        assert result.error is None

    @skip_google
    def test_google_usage_metadata_is_object(self):
        """Test that Google usage metadata is handled correctly."""
        from api.google_research import GoogleResearcher

        researcher = GoogleResearcher(os.getenv("GEMINI_API_KEY"))
        result = researcher.basic_research(
            "Brief overview",
            "Netflix"
        )

        # Google returns usage as object, not dict
        if result.usage:
            # Should not raise AttributeError
            assert hasattr(result.usage, 'prompt_token_count') or isinstance(result.usage, dict)


@pytest.mark.integration
@pytest.mark.slow
class TestXAIIntegration:
    """Integration tests for xAI provider."""

    @skip_xai
    def test_xai_basic_research(self):
        """Test xAI basic research returns valid result."""
        from api.xai_research import XAIResearcher

        researcher = XAIResearcher(os.getenv("XAI_API_KEY"))
        result = researcher.basic_research(
            "What is the company's competitive advantage?",
            "NVIDIA"
        )

        assert result.provider == "xai"
        assert result.mode == "basic"
        assert result.text
        assert result.error is None

    @skip_xai
    def test_xai_returns_citations(self):
        """Test that xAI returns citations from search."""
        from api.xai_research import XAIResearcher

        researcher = XAIResearcher(os.getenv("XAI_API_KEY"))
        result = researcher.basic_research(
            "Latest news about the company",
            "Meta"
        )

        assert isinstance(result.citations, list)


@pytest.mark.integration
@pytest.mark.slow
class TestPerplexityIntegration:
    """Integration tests for Perplexity provider."""

    @skip_perplexity
    def test_perplexity_basic_research(self):
        """Test Perplexity basic research returns valid result."""
        from api.perplexity_research import PerplexityResearcher

        researcher = PerplexityResearcher(os.getenv("PERPLEXITY_API_KEY"))
        result = researcher.basic_research(
            "What is the company's revenue model?",
            "Spotify"
        )

        assert result.provider == "perplexity"
        assert result.mode == "basic"
        assert result.text
        assert result.error is None

    @skip_perplexity
    def test_perplexity_returns_citations(self):
        """Test that Perplexity returns citations."""
        from api.perplexity_research import PerplexityResearcher

        researcher = PerplexityResearcher(os.getenv("PERPLEXITY_API_KEY"))
        result = researcher.basic_research(
            "Recent company developments",
            "Adobe"
        )

        # Perplexity should always return citations
        assert isinstance(result.citations, list)
        assert len(result.citations) > 0  # Perplexity typically provides citations


@pytest.mark.integration
@pytest.mark.slow
class TestMultiProviderResearch:
    """Integration tests for running research across multiple providers."""

    def test_research_engine_parallel_execution(self):
        """Test that research engine can run multiple providers in parallel."""
        from api.research_engine import ResearchEngine

        engine = ResearchEngine()
        status = engine.setup_researchers()

        # Skip if no providers available
        available_providers = [p for p, available in status.items() if available]
        if not available_providers:
            pytest.skip("No providers available for integration test")

        results = engine.run_research(
            "Test Company",
            "leadership_team_dynamics",
            mode="basic",
            providers=available_providers[:2]  # Use at most 2 to limit costs
        )

        assert len(results) > 0
        for provider, result in results.items():
            assert result.provider == provider
            # Should have either content or an error
            assert result.text or result.error


@pytest.mark.integration
class TestProviderAvailability:
    """Tests to check which providers are currently available."""

    def test_print_provider_availability(self):
        """Print which providers are available for testing."""
        providers = {
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic": "ANTHROPIC_API_KEY",
            "Google": "GEMINI_API_KEY",
            "xAI": "XAI_API_KEY",
            "Perplexity": "PERPLEXITY_API_KEY"
        }

        print("\n=== Provider Availability ===")
        for name, key in providers.items():
            available = has_api_key(key)
            status = "AVAILABLE" if available else "NOT CONFIGURED"
            print(f"  {name}: {status}")

        # This test always passes - it's informational
        assert True
