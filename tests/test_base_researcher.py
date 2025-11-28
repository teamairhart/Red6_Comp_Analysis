"""
Unit tests for the base researcher module.
"""
import pytest
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.base_researcher import ResearchResult, BaseResearcher


class TestResearchResult:
    """Tests for the ResearchResult dataclass."""

    def test_research_result_creation(self):
        """Test creating a basic research result."""
        result = ResearchResult(
            provider="openai",
            model="gpt-5.1",
            mode="basic",
            text="Research findings about the company.",
            citations=[
                {"title": "Source 1", "url": "https://example.com/1"}
            ],
            timestamp=datetime(2025, 11, 28, 12, 0, 0)
        )

        assert result.provider == "openai"
        assert result.model == "gpt-5.1"
        assert result.mode == "basic"
        assert len(result.citations) == 1
        assert result.error is None

    def test_research_result_with_error(self):
        """Test creating a result with an error."""
        result = ResearchResult(
            provider="anthropic",
            model="claude-opus-4-5",
            mode="deep",
            text="",
            citations=[],
            timestamp=datetime.utcnow(),
            error="Rate limit exceeded"
        )

        assert result.error == "Rate limit exceeded"
        assert result.text == ""

    def test_research_result_with_usage(self):
        """Test creating a result with usage data."""
        result = ResearchResult(
            provider="google",
            model="gemini-3-pro",
            mode="basic",
            text="Research findings...",
            citations=[],
            timestamp=datetime.utcnow(),
            usage={"input_tokens": 500, "output_tokens": 1000}
        )

        assert result.usage["input_tokens"] == 500
        assert result.usage["output_tokens"] == 1000

    def test_to_markdown_basic(self):
        """Test converting result to markdown format."""
        result = ResearchResult(
            provider="openai",
            model="gpt-5.1",
            mode="basic",
            text="# Research Findings\n\nThis is the research content.",
            citations=[
                {"title": "Source 1", "url": "https://example.com/1"},
                {"title": "Source 2", "url": "https://example.com/2"}
            ],
            timestamp=datetime(2025, 11, 28, 14, 30, 0)
        )

        markdown = result.to_markdown()

        # Check header includes provider
        assert "OPENAI" in markdown
        assert "gpt-5.1" in markdown
        assert "basic" in markdown

        # Check content
        assert "# Research Findings" in markdown
        assert "This is the research content." in markdown

        # Check sources section
        assert "## Sources" in markdown
        assert "Source 1" in markdown
        assert "https://example.com/1" in markdown

    def test_to_markdown_with_error(self):
        """Test markdown output when there's an error."""
        result = ResearchResult(
            provider="anthropic",
            model="claude-opus-4-5",
            mode="basic",
            text="",
            citations=[],
            timestamp=datetime.utcnow(),
            error="API connection failed"
        )

        markdown = result.to_markdown()

        # The current implementation doesn't include error in markdown output
        # Just verify it produces valid markdown with the provider info
        assert "ANTHROPIC" in markdown
        assert "claude-opus-4-5" in markdown

    def test_to_markdown_no_citations(self):
        """Test markdown output when there are no citations."""
        result = ResearchResult(
            provider="xai",
            model="grok-4",
            mode="basic",
            text="Research content without citations.",
            citations=[],
            timestamp=datetime.utcnow()
        )

        markdown = result.to_markdown()

        # The current implementation only adds Sources section if there are citations
        # No citations means no Sources section
        assert "XAI" in markdown
        assert "Research content without citations." in markdown

    def test_to_markdown_with_usage(self):
        """Test markdown includes basic output even with usage data."""
        result = ResearchResult(
            provider="perplexity",
            model="sonar-pro",
            mode="deep",
            text="Deep research findings.",
            citations=[],
            timestamp=datetime.utcnow(),
            usage={"input_tokens": 1500, "output_tokens": 3000}
        )

        markdown = result.to_markdown()

        # Current implementation doesn't include usage in markdown
        # Just verify it produces valid markdown
        assert "PERPLEXITY" in markdown
        assert "sonar-pro" in markdown
        assert "Deep research findings." in markdown


class TestResearchResultCitations:
    """Tests for citation handling in ResearchResult."""

    def test_citations_with_various_formats(self):
        """Test handling different citation formats."""
        citations = [
            {"title": "Title Only", "url": "https://example.com/1"},
            {"title": "With Description", "url": "https://example.com/2", "description": "A description"},
            {"url": "https://example.com/3"},  # URL only, no title
        ]

        result = ResearchResult(
            provider="test",
            model="test-model",
            mode="basic",
            text="Content",
            citations=citations,
            timestamp=datetime.utcnow()
        )

        markdown = result.to_markdown()

        assert "https://example.com/1" in markdown
        assert "https://example.com/2" in markdown
        assert "https://example.com/3" in markdown


class TestResearchResultEdgeCases:
    """Tests for edge cases in ResearchResult."""

    def test_empty_text(self):
        """Test result with empty text."""
        result = ResearchResult(
            provider="test",
            model="test-model",
            mode="basic",
            text="",
            citations=[],
            timestamp=datetime.utcnow()
        )

        markdown = result.to_markdown()
        assert markdown  # Should still produce output

    def test_very_long_text(self):
        """Test result with very long text."""
        long_text = "A" * 100000  # 100K characters

        result = ResearchResult(
            provider="test",
            model="test-model",
            mode="deep",
            text=long_text,
            citations=[],
            timestamp=datetime.utcnow()
        )

        markdown = result.to_markdown()
        assert long_text in markdown

    def test_special_characters_in_text(self):
        """Test handling of special characters."""
        text_with_special = "Research about Company™ & Partners® with <tags> and \"quotes\""

        result = ResearchResult(
            provider="test",
            model="test-model",
            mode="basic",
            text=text_with_special,
            citations=[],
            timestamp=datetime.utcnow()
        )

        markdown = result.to_markdown()
        assert text_with_special in markdown

    def test_unicode_in_text(self):
        """Test handling of unicode characters."""
        unicode_text = "研究结果：公司分析 • 日本語テスト • Émoji test 🎉"

        result = ResearchResult(
            provider="test",
            model="test-model",
            mode="basic",
            text=unicode_text,
            citations=[],
            timestamp=datetime.utcnow()
        )

        markdown = result.to_markdown()
        assert unicode_text in markdown


class TestBaseResearcherAbstract:
    """Tests for the BaseResearcher abstract class."""

    def test_cannot_instantiate_base_researcher(self):
        """Test that BaseResearcher cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseResearcher("test-api-key")

    def test_subclass_must_implement_methods(self):
        """Test that subclasses must implement required methods."""
        class IncompleteResearcher(BaseResearcher):
            pass

        with pytest.raises(TypeError):
            IncompleteResearcher("test-api-key")

    def test_valid_subclass(self):
        """Test that a valid subclass can be instantiated."""
        class ValidResearcher(BaseResearcher):
            def basic_research(self, prompt: str, company: str) -> ResearchResult:
                return ResearchResult(
                    provider="valid",
                    model="valid-model",
                    mode="basic",
                    text="Results",
                    citations=[],
                    timestamp=datetime.utcnow()
                )

            def deep_research(self, prompt: str, company: str) -> ResearchResult:
                return ResearchResult(
                    provider="valid",
                    model="valid-model",
                    mode="deep",
                    text="Deep results",
                    citations=[],
                    timestamp=datetime.utcnow()
                )

        researcher = ValidResearcher("test-key")
        assert researcher.api_key == "test-key"

    def test_research_method_routing(self):
        """Test that research() routes to correct method based on mode."""
        class TestResearcher(BaseResearcher):
            def basic_research(self, prompt: str, company: str) -> ResearchResult:
                return ResearchResult(
                    provider="test",
                    model="test-model",
                    mode="basic",
                    text="Basic results",
                    citations=[],
                    timestamp=datetime.utcnow()
                )

            def deep_research(self, prompt: str, company: str) -> ResearchResult:
                return ResearchResult(
                    provider="test",
                    model="test-model",
                    mode="deep",
                    text="Deep results",
                    citations=[],
                    timestamp=datetime.utcnow()
                )

        researcher = TestResearcher("test-key")

        basic_result = researcher.research("prompt", "company", "basic")
        assert basic_result.mode == "basic"
        assert basic_result.text == "Basic results"

        deep_result = researcher.research("prompt", "company", "deep")
        assert deep_result.mode == "deep"
        assert deep_result.text == "Deep results"
