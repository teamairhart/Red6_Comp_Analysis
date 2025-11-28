"""
Unit tests for the cost calculator module.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cost_calculator import (
    CostCalculator,
    CostEstimate,
    calculate_query_cost,
    format_cost_table,
    PRICING,
    DEFAULT_PRICING
)
from api.base_researcher import ResearchResult


class TestCostEstimate:
    """Tests for the CostEstimate dataclass."""

    def test_cost_estimate_creation(self):
        """Test creating a basic cost estimate."""
        estimate = CostEstimate(
            provider="anthropic",
            model="claude-opus-4-5-20251101",
            input_tokens=1000,
            output_tokens=500,
            input_cost=0.015,
            output_cost=0.0375
        )

        assert estimate.provider == "anthropic"
        assert estimate.model == "claude-opus-4-5-20251101"
        assert estimate.input_tokens == 1000
        assert estimate.output_tokens == 500
        assert estimate.total_cost == 0.0525  # 0.015 + 0.0375

    def test_cost_estimate_with_search_cost(self):
        """Test cost estimate including search costs."""
        estimate = CostEstimate(
            provider="xai",
            model="grok-4-0709",
            input_tokens=1000,
            output_tokens=500,
            input_cost=0.003,
            output_cost=0.0075,
            search_cost=0.50  # 20 sources * $0.025
        )

        assert estimate.search_cost == 0.50
        assert estimate.total_cost == 0.5105  # 0.003 + 0.0075 + 0.50


class TestCostCalculator:
    """Tests for the CostCalculator class."""

    def test_calculator_initialization(self):
        """Test calculator initializes with empty session."""
        calc = CostCalculator()

        assert calc.session_costs == []
        assert calc.warning_threshold == 5.00
        assert calc.get_session_total() == 0.0

    def test_calculate_cost_anthropic(self):
        """Test cost calculation for Anthropic Claude."""
        calc = CostCalculator()
        estimate = calc.calculate_cost(
            provider="anthropic",
            model="claude-opus-4-5-20251101",
            input_tokens=1_000_000,  # 1M tokens
            output_tokens=1_000_000
        )

        assert estimate.provider == "anthropic"
        assert estimate.input_cost == 15.00  # $15 per 1M
        assert estimate.output_cost == 75.00  # $75 per 1M
        assert estimate.total_cost == 90.00

    def test_calculate_cost_openai(self):
        """Test cost calculation for OpenAI."""
        calc = CostCalculator()
        estimate = calc.calculate_cost(
            provider="openai",
            model="gpt-5.1",
            input_tokens=1_000_000,
            output_tokens=1_000_000
        )

        assert estimate.input_cost == 2.50
        assert estimate.output_cost == 10.00
        assert estimate.total_cost == 12.50

    def test_calculate_cost_google(self):
        """Test cost calculation for Google Gemini."""
        calc = CostCalculator()
        estimate = calc.calculate_cost(
            provider="google",
            model="gemini-3-pro-preview",
            input_tokens=1_000_000,
            output_tokens=1_000_000
        )

        assert estimate.input_cost == 1.25
        assert estimate.output_cost == 5.00
        assert estimate.total_cost == 6.25

    def test_calculate_cost_xai_with_search(self):
        """Test xAI cost calculation with search sources."""
        calc = CostCalculator()
        estimate = calc.calculate_cost(
            provider="xai",
            model="grok-4-0709",
            input_tokens=100_000,
            output_tokens=50_000,
            search_sources=20
        )

        expected_input = (100_000 / 1_000_000) * 3.00  # $0.30
        expected_output = (50_000 / 1_000_000) * 15.00  # $0.75
        expected_search = 20 * 0.025  # $0.50

        assert abs(estimate.input_cost - expected_input) < 0.001
        assert abs(estimate.output_cost - expected_output) < 0.001
        assert abs(estimate.search_cost - expected_search) < 0.001

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation falls back to defaults for unknown models."""
        calc = CostCalculator()
        estimate = calc.calculate_cost(
            provider="unknown_provider",
            model="unknown-model",
            input_tokens=1_000_000,
            output_tokens=1_000_000
        )

        assert estimate.input_cost == DEFAULT_PRICING["input"]
        assert estimate.output_cost == DEFAULT_PRICING["output"]

    def test_add_to_session(self):
        """Test adding estimates to session tracking."""
        calc = CostCalculator()

        estimate1 = calc.calculate_cost("openai", "gpt-5.1", 100_000, 50_000)
        estimate2 = calc.calculate_cost("anthropic", "claude-opus-4-5-20251101", 100_000, 50_000)

        calc.add_to_session(estimate1)
        calc.add_to_session(estimate2)

        assert len(calc.session_costs) == 2
        assert calc.get_session_total() == estimate1.total_cost + estimate2.total_cost

    def test_session_summary(self):
        """Test getting session summary by provider."""
        calc = CostCalculator()

        estimate1 = calc.calculate_cost("openai", "gpt-5.1", 100_000, 50_000)
        estimate2 = calc.calculate_cost("openai", "gpt-5.1", 200_000, 100_000)
        estimate3 = calc.calculate_cost("anthropic", "claude-opus-4-5-20251101", 50_000, 25_000)

        calc.add_to_session(estimate1)
        calc.add_to_session(estimate2)
        calc.add_to_session(estimate3)

        summary = calc.get_session_summary()

        assert summary["query_count"] == 3
        assert "openai" in summary["by_provider"]
        assert "anthropic" in summary["by_provider"]
        assert summary["by_provider"]["openai"]["queries"] == 2
        assert summary["by_provider"]["anthropic"]["queries"] == 1

    def test_threshold_warning_not_exceeded(self):
        """Test no warning when under threshold."""
        calc = CostCalculator()
        calc.warning_threshold = 10.00

        estimate = calc.calculate_cost("google", "gemini-3-pro-preview", 100_000, 50_000)
        calc.add_to_session(estimate)

        warning = calc.check_threshold_warning()
        assert warning is None

    def test_threshold_warning_exceeded(self):
        """Test warning when threshold exceeded."""
        calc = CostCalculator()
        calc.warning_threshold = 0.01  # Very low threshold

        estimate = calc.calculate_cost("anthropic", "claude-opus-4-5-20251101", 100_000, 50_000)
        calc.add_to_session(estimate)

        warning = calc.check_threshold_warning()
        assert warning is not None
        assert "$0.01" in warning

    def test_reset_session(self):
        """Test resetting session clears all data."""
        calc = CostCalculator()

        estimate = calc.calculate_cost("openai", "gpt-5.1", 100_000, 50_000)
        calc.add_to_session(estimate)

        assert len(calc.session_costs) == 1

        calc.reset_session()

        assert len(calc.session_costs) == 0
        assert calc.get_session_total() == 0.0


class TestCalculateQueryCost:
    """Tests for the calculate_query_cost function."""

    def test_calculate_query_cost_dict_usage(self):
        """Test cost calculation with dict-style usage (OpenAI/Anthropic)."""
        results = {
            "openai": ResearchResult(
                provider="openai",
                model="gpt-5.1",
                mode="basic",
                text="Research results...",
                citations=[],
                timestamp=datetime.utcnow(),
                usage={"input_tokens": 1000, "output_tokens": 500}
            ),
            "anthropic": ResearchResult(
                provider="anthropic",
                model="claude-opus-4-5-20251101",
                mode="basic",
                text="Research results...",
                citations=[],
                timestamp=datetime.utcnow(),
                usage={"input_tokens": 800, "output_tokens": 400}
            )
        }

        costs = calculate_query_cost(results)

        assert "openai" in costs["by_provider"]
        assert "anthropic" in costs["by_provider"]
        assert costs["total"]["input_tokens"] == 1800
        assert costs["total"]["output_tokens"] == 900
        assert costs["total"]["cost"] > 0

    def test_calculate_query_cost_object_usage(self):
        """Test cost calculation with object-style usage (Google)."""
        # Create a mock usage object like Google returns
        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 500
        mock_usage.candidates_token_count = 250

        results = {
            "google": ResearchResult(
                provider="google",
                model="gemini-3-pro-preview",
                mode="basic",
                text="Research results...",
                citations=[],
                timestamp=datetime.utcnow(),
                usage=mock_usage
            )
        }

        costs = calculate_query_cost(results)

        assert "google" in costs["by_provider"]
        assert costs["by_provider"]["google"]["input_tokens"] == 500
        assert costs["by_provider"]["google"]["output_tokens"] == 250

    def test_calculate_query_cost_no_usage(self):
        """Test handling results without usage data."""
        results = {
            "openai": ResearchResult(
                provider="openai",
                model="gpt-5.1",
                mode="basic",
                text="Research results...",
                citations=[],
                timestamp=datetime.utcnow(),
                usage=None
            )
        }

        costs = calculate_query_cost(results)

        assert costs["total"]["input_tokens"] == 0
        assert costs["total"]["output_tokens"] == 0
        assert costs["total"]["cost"] == 0.0

    def test_calculate_query_cost_prompt_tokens_fallback(self):
        """Test fallback to prompt_tokens/completion_tokens naming."""
        results = {
            "openai": ResearchResult(
                provider="openai",
                model="gpt-5.1",
                mode="basic",
                text="Research results...",
                citations=[],
                timestamp=datetime.utcnow(),
                usage={"prompt_tokens": 1000, "completion_tokens": 500}
            )
        }

        costs = calculate_query_cost(results)

        assert costs["by_provider"]["openai"]["input_tokens"] == 1000
        assert costs["by_provider"]["openai"]["output_tokens"] == 500


class TestFormatCostTable:
    """Tests for the format_cost_table function."""

    def test_format_cost_table_basic(self):
        """Test basic cost table formatting."""
        costs = {
            "by_provider": {
                "openai": {
                    "model": "gpt-5.1",
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "total_cost": 0.025
                },
                "anthropic": {
                    "model": "claude-opus-4-5-20251101",
                    "input_tokens": 800,
                    "output_tokens": 400,
                    "total_cost": 0.042
                }
            },
            "total": {
                "input_tokens": 1800,
                "output_tokens": 900,
                "cost": 0.067
            }
        }

        table = format_cost_table(costs)

        assert "| Provider |" in table
        assert "OPENAI" in table
        assert "ANTHROPIC" in table
        assert "**TOTAL**" in table
        assert "$0.0670" in table or "$0.067" in table

    def test_format_cost_table_empty(self):
        """Test formatting empty cost data."""
        costs = {
            "by_provider": {},
            "total": {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0
            }
        }

        table = format_cost_table(costs)

        assert "| Provider |" in table
        assert "**TOTAL**" in table


class TestPricingConfiguration:
    """Tests for pricing configuration."""

    def test_all_providers_have_pricing(self):
        """Verify all expected providers have pricing defined."""
        expected_providers = ["anthropic", "openai", "google", "xai", "perplexity"]

        for provider in expected_providers:
            assert provider in PRICING, f"Missing pricing for {provider}"

    def test_pricing_structure(self):
        """Verify pricing structure is correct for each provider."""
        for provider, models in PRICING.items():
            if provider == "xai":
                # xAI has special search_cost_per_source
                assert "search_cost_per_source" in models

            for model, prices in models.items():
                if model != "search_cost_per_source":
                    assert "input" in prices, f"Missing input price for {provider}/{model}"
                    assert "output" in prices, f"Missing output price for {provider}/{model}"
                    assert prices["input"] > 0, f"Invalid input price for {provider}/{model}"
                    assert prices["output"] > 0, f"Invalid output price for {provider}/{model}"

    def test_default_pricing_exists(self):
        """Verify default pricing is defined."""
        assert "input" in DEFAULT_PRICING
        assert "output" in DEFAULT_PRICING
        assert DEFAULT_PRICING["input"] > 0
        assert DEFAULT_PRICING["output"] > 0
