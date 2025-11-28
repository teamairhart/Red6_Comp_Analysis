"""
Unit tests for the research engine module.
"""
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.research_engine import ResearchEngine, ResearchJob
from api.base_researcher import ResearchResult


class TestResearchJob:
    """Tests for the ResearchJob dataclass."""

    def test_research_job_creation(self):
        """Test creating a research job."""
        job = ResearchJob(
            company="BAE Systems",
            prompt_name="leadership_team_dynamics",
            prompt_content="Research BAE Systems for...",
            mode="basic",
            output_format="markdown"
        )

        assert job.company == "BAE Systems"
        assert job.prompt_name == "leadership_team_dynamics"
        assert job.mode == "basic"
        assert job.output_format == "markdown"


class TestResearchEngineInit:
    """Tests for ResearchEngine initialization."""

    def test_engine_initialization_default_paths(self):
        """Test engine initializes with default paths."""
        engine = ResearchEngine()

        assert engine.project_root.exists()
        assert engine.prompts_dir == engine.project_root / "prompts"
        assert engine.reports_dir == engine.project_root / "reports"
        assert engine.companies_file == engine.project_root / "companies.csv"

    def test_engine_initialization_custom_root(self, tmp_path):
        """Test engine with custom project root."""
        engine = ResearchEngine(project_root=str(tmp_path))

        assert engine.project_root == tmp_path
        assert engine.prompts_dir == tmp_path / "prompts"


class TestResearchEngineCompanies:
    """Tests for company loading functionality."""

    def test_get_companies(self, tmp_path):
        """Test loading companies from CSV."""
        # Create minimal project structure
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()

        # Create companies CSV directly
        csv_content = """company,website
BAE Systems,https://www.baesystems.com
Elbit Systems,https://www.elbitsystems.com
Thales,https://www.thalesgroup.com
"""
        (tmp_path / "companies.csv").write_text(csv_content)

        engine = ResearchEngine(project_root=str(tmp_path))
        companies = engine.get_companies()

        assert len(companies) == 3
        assert companies[0]["name"] == "BAE Systems"
        assert companies[0]["website"] == "https://www.baesystems.com"

    def test_get_companies_empty_file(self, tmp_path):
        """Test handling empty companies file."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))
        companies = engine.get_companies()

        assert companies == []

    def test_get_companies_missing_file(self, tmp_path):
        """Test handling missing companies file."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()

        engine = ResearchEngine(project_root=str(tmp_path))
        companies = engine.get_companies()

        assert companies == []


class TestResearchEnginePrompts:
    """Tests for prompt loading functionality."""

    def test_get_prompts(self, sample_prompt_file, tmp_path):
        """Test loading available prompts."""
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))
        prompts = engine.get_prompts()

        assert len(prompts) == 1
        assert prompts[0]["name"] == "leadership_team_dynamics"
        assert prompts[0]["filename"] == "leadership_team_dynamics.md"

    def test_get_prompts_multiple(self, tmp_path):
        """Test loading multiple prompts."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        # Create multiple prompt files
        (tmp_path / "prompts" / "prompt_a.md").write_text("Prompt A content")
        (tmp_path / "prompts" / "prompt_b.md").write_text("Prompt B content")
        (tmp_path / "prompts" / "prompt_c.md").write_text("Prompt C content")

        engine = ResearchEngine(project_root=str(tmp_path))
        prompts = engine.get_prompts()

        assert len(prompts) == 3
        # Should be sorted alphabetically
        names = [p["name"] for p in prompts]
        assert names == sorted(names)

    def test_load_prompt_content(self, sample_prompt_file, tmp_path):
        """Test loading prompt content."""
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))
        content = engine.load_prompt("leadership_team_dynamics")

        assert "[COMPANY NAME]" in content
        assert "executive changes" in content

    def test_load_prompt_not_found(self, tmp_path):
        """Test error when prompt not found."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))

        with pytest.raises(FileNotFoundError) as exc_info:
            engine.load_prompt("nonexistent_prompt")

        assert "nonexistent_prompt" in str(exc_info.value)


class TestResearchEngineProviderSetup:
    """Tests for provider setup functionality."""

    def test_setup_researchers_no_keys(self, tmp_path, mock_env_no_keys):
        """Test setup with no API keys configured."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))
        status = engine.setup_researchers()

        # All providers should be unavailable
        assert all(not available for available in status.values())
        assert len(engine.researchers) == 0

    def test_setup_researchers_placeholder_keys(self, tmp_path, monkeypatch):
        """Test setup ignores placeholder API keys."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        # Set placeholder keys
        monkeypatch.setenv("OPENAI_API_KEY", "sk-your-key-here")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-your-key-here")
        monkeypatch.setenv("GEMINI_API_KEY", "your-gemini-key")
        monkeypatch.setenv("XAI_API_KEY", "xai-your-key-here")
        monkeypatch.setenv("PERPLEXITY_API_KEY", "pplx-your-key-here")

        engine = ResearchEngine(project_root=str(tmp_path))
        status = engine.setup_researchers()

        # Placeholder keys should be rejected
        assert all(not available for available in status.values())


class TestResearchEngineSaveResults:
    """Tests for saving research results."""

    def test_save_results_creates_directory(self, tmp_path):
        """Test saving results creates proper directory structure."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))

        results = {
            "openai": ResearchResult(
                provider="openai",
                model="gpt-5.1",
                mode="basic",
                text="Research findings...",
                citations=[],
                timestamp=datetime.utcnow()
            )
        }

        timestamp = datetime(2025, 11, 28, 14, 30, 22)
        saved_files, timestamp_str = engine.save_results(
            results, "Test Company", "test_prompt", timestamp
        )

        assert len(saved_files) == 1
        assert timestamp_str == "2025-11-28_143022"

        # Check directory was created
        expected_dir = tmp_path / "reports" / "Test Company" / timestamp_str
        assert expected_dir.exists()

        # Check file was saved
        assert (expected_dir / "test_prompt-openai.md").exists()

        # Check metadata file
        assert (expected_dir / "metadata.txt").exists()

    def test_save_results_multiple_providers(self, tmp_path):
        """Test saving results from multiple providers."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))

        results = {
            "openai": ResearchResult(
                provider="openai",
                model="gpt-5.1",
                mode="basic",
                text="OpenAI findings...",
                citations=[],
                timestamp=datetime.utcnow()
            ),
            "anthropic": ResearchResult(
                provider="anthropic",
                model="claude-opus-4-5",
                mode="basic",
                text="Anthropic findings...",
                citations=[],
                timestamp=datetime.utcnow()
            ),
            "google": ResearchResult(
                provider="google",
                model="gemini-3-pro",
                mode="basic",
                text="Google findings...",
                citations=[],
                timestamp=datetime.utcnow()
            )
        }

        saved_files, _ = engine.save_results(results, "Multi Provider Test", "test_prompt")

        assert len(saved_files) == 3

    def test_save_results_creates_latest_symlink(self, tmp_path):
        """Test that latest symlink is created."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        engine = ResearchEngine(project_root=str(tmp_path))

        results = {
            "openai": ResearchResult(
                provider="openai",
                model="gpt-5.1",
                mode="basic",
                text="Research...",
                citations=[],
                timestamp=datetime.utcnow()
            )
        }

        engine.save_results(results, "Symlink Test", "test_prompt")

        latest_link = tmp_path / "reports" / "Symlink Test" / "latest"
        assert latest_link.is_symlink()


class TestResearchEngineRunResearch:
    """Tests for running research with mocked providers."""

    def test_run_research_parallel_execution(self, tmp_path):
        """Test that research runs in parallel across providers."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")
        (tmp_path / "prompts" / "test_prompt.md").write_text("Research [COMPANY NAME]")

        engine = ResearchEngine(project_root=str(tmp_path))

        # Create mock researchers
        mock_openai = MagicMock()
        mock_openai.research.return_value = ResearchResult(
            provider="openai",
            model="gpt-5.1",
            mode="basic",
            text="OpenAI results",
            citations=[],
            timestamp=datetime.utcnow()
        )

        mock_anthropic = MagicMock()
        mock_anthropic.research.return_value = ResearchResult(
            provider="anthropic",
            model="claude",
            mode="basic",
            text="Anthropic results",
            citations=[],
            timestamp=datetime.utcnow()
        )

        engine.researchers = {
            "openai": mock_openai,
            "anthropic": mock_anthropic
        }

        results = engine.run_research("Test Company", "test_prompt", "basic")

        assert "openai" in results
        assert "anthropic" in results
        assert results["openai"].text == "OpenAI results"
        assert results["anthropic"].text == "Anthropic results"

        # Verify research was called on both
        mock_openai.research.assert_called_once()
        mock_anthropic.research.assert_called_once()

    def test_run_research_specific_providers(self, tmp_path):
        """Test running research with specific providers only."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")
        (tmp_path / "prompts" / "test_prompt.md").write_text("Research [COMPANY NAME]")

        engine = ResearchEngine(project_root=str(tmp_path))

        mock_openai = MagicMock()
        mock_openai.research.return_value = ResearchResult(
            provider="openai",
            model="gpt-5.1",
            mode="basic",
            text="OpenAI results",
            citations=[],
            timestamp=datetime.utcnow()
        )

        mock_anthropic = MagicMock()

        engine.researchers = {
            "openai": mock_openai,
            "anthropic": mock_anthropic
        }

        # Only run with openai
        results = engine.run_research(
            "Test Company", "test_prompt", "basic",
            providers=["openai"]
        )

        assert "openai" in results
        assert "anthropic" not in results
        mock_anthropic.research.assert_not_called()

    def test_run_research_handles_provider_error(self, tmp_path):
        """Test graceful handling of provider errors."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")
        (tmp_path / "prompts" / "test_prompt.md").write_text("Research [COMPANY NAME]")

        engine = ResearchEngine(project_root=str(tmp_path))

        mock_openai = MagicMock()
        mock_openai.research.side_effect = Exception("API Error")

        engine.researchers = {"openai": mock_openai}

        results = engine.run_research("Test Company", "test_prompt", "basic")

        assert "openai" in results
        assert results["openai"].error == "API Error"
        assert results["openai"].text == ""


class TestResearchEngineEnvLoading:
    """Tests for environment variable loading."""

    def test_load_env_from_file(self, tmp_path):
        """Test loading environment from .env file."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        # Create .env file
        env_content = """
OPENAI_API_KEY=test-openai-key
ANTHROPIC_API_KEY=test-anthropic-key
"""
        (tmp_path / ".env").write_text(env_content)

        # Clear any existing env vars
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)

        engine = ResearchEngine(project_root=str(tmp_path))

        assert os.environ.get("OPENAI_API_KEY") == "test-openai-key"
        assert os.environ.get("ANTHROPIC_API_KEY") == "test-anthropic-key"

    def test_load_env_ignores_comments(self, tmp_path):
        """Test that .env loading ignores comments."""
        (tmp_path / "prompts").mkdir()
        (tmp_path / "reports").mkdir()
        (tmp_path / "companies.csv").write_text("company,website\n")

        env_content = """
# This is a comment
OPENAI_API_KEY=test-key
# Another comment
"""
        (tmp_path / ".env").write_text(env_content)

        os.environ.pop("OPENAI_API_KEY", None)

        engine = ResearchEngine(project_root=str(tmp_path))

        assert os.environ.get("OPENAI_API_KEY") == "test-key"
