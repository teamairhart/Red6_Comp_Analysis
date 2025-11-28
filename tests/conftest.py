"""
Pytest configuration and shared fixtures for competitive analysis tests.
"""
import pytest
import os
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.base_researcher import ResearchResult


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def sample_research_result():
    """Create a sample ResearchResult for testing."""
    return ResearchResult(
        provider="test_provider",
        model="test-model-1.0",
        mode="basic",
        text="This is sample research text about Test Company.",
        citations=[
            {"title": "Test Source 1", "url": "https://example.com/1"},
            {"title": "Test Source 2", "url": "https://example.com/2"},
        ],
        timestamp=datetime(2025, 11, 28, 12, 0, 0),
        usage={"input_tokens": 100, "output_tokens": 200},
        error=None
    )


@pytest.fixture
def sample_research_result_with_error():
    """Create a sample ResearchResult with an error."""
    return ResearchResult(
        provider="test_provider",
        model="test-model-1.0",
        mode="basic",
        text="",
        citations=[],
        timestamp=datetime(2025, 11, 28, 12, 0, 0),
        usage=None,
        error="API rate limit exceeded"
    )


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    mock_response = MagicMock()
    mock_response.output_text = "Research findings about the company..."
    mock_response.usage.input_tokens = 500
    mock_response.usage.output_tokens = 1000
    return mock_response


@pytest.fixture
def mock_anthropic_response():
    """Create a mock Anthropic API response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Research findings from Claude...")]
    mock_response.usage.input_tokens = 400
    mock_response.usage.output_tokens = 800
    return mock_response


@pytest.fixture
def mock_google_response():
    """Create a mock Google Gemini API response."""
    mock_response = MagicMock()
    mock_response.text = "Research findings from Gemini..."
    mock_response.usage_metadata.prompt_token_count = 300
    mock_response.usage_metadata.candidates_token_count = 600
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].grounding_metadata = None
    return mock_response


@pytest.fixture
def mock_xai_response():
    """Create a mock xAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Research findings from Grok..."
    mock_response.usage.prompt_tokens = 350
    mock_response.usage.completion_tokens = 700
    return mock_response


@pytest.fixture
def sample_companies_csv(tmp_path):
    """Create a temporary companies.csv file."""
    csv_content = """company,website
BAE Systems,https://www.baesystems.com
Elbit Systems,https://www.elbitsystems.com
Thales,https://www.thalesgroup.com
"""
    csv_file = tmp_path / "companies.csv"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def sample_prompt_file(tmp_path):
    """Create a temporary prompt file."""
    prompt_content = """# Leadership Team Dynamics

Research [COMPANY NAME] for the following information:

1. Recent executive changes
2. Board composition
3. Leadership strategy
"""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "leadership_team_dynamics.md"
    prompt_file.write_text(prompt_content)
    return prompts_dir


@pytest.fixture
def temp_reports_dir(tmp_path):
    """Create a temporary reports directory."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    return reports_dir


@pytest.fixture
def mock_env_with_keys(monkeypatch):
    """Set up mock environment variables with API keys."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("XAI_API_KEY", "xai-test-key")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "pplx-test-key")


@pytest.fixture
def mock_env_no_keys(monkeypatch):
    """Set up mock environment without API keys."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)


# Markers for different test types
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires API keys)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
