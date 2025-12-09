"""
Cost Calculator for LLM API Usage.

Provides estimated costs based on token usage and current pricing.
Pricing is approximate and should be verified against official pricing pages.
"""
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime


# Pricing per 1M tokens (as of November 2025)
# These are estimates - verify with official pricing
PRICING = {
    "anthropic": {
        "claude-opus-4-5-20251101": {
            "input": 15.00,   # $15 per 1M input tokens
            "output": 75.00,  # $75 per 1M output tokens
        },
        "claude-sonnet-4-5-20250929": {
            "input": 3.00,
            "output": 15.00,
        },
    },
    "openai": {
        "gpt-5.1": {
            "input": 2.50,    # $2.50 per 1M input tokens
            "output": 10.00,  # $10 per 1M output tokens
        },
        "gpt-4o": {
            "input": 2.50,
            "output": 10.00,
        },
    },
    "google": {
        "gemini-3-pro-preview": {
            "input": 2.00,    # $2 per 1M input tokens (<=200k context)
            "output": 12.00,  # $12 per 1M output tokens
        },
        "gemini-2.0-flash": {
            "input": 0.10,
            "output": 0.40,
        },
    },
    "xai": {
        "grok-4-0709": {
            "input": 3.00,    # $3 per 1M input tokens
            "output": 15.00,  # $15 per 1M output tokens
        },
        "grok-4-fast": {
            "input": 5.00,    # $5 per 1M input tokens
            "output": 25.00,  # $25 per 1M output tokens
        },
        # Additional: xAI charges $0.025 per search source used
        "search_cost_per_source": 0.025,
    },
    "perplexity": {
        "sonar-pro": {
            "input": 3.00,    # $3 per 1M input tokens
            "output": 15.00,  # $15 per 1M output tokens
            # Search cost included in token pricing
        },
        "sonar-deep-research": {
            "input": 2.00,    # $2 per 1M input tokens
            "output": 8.00,   # $8 per 1M output tokens
            # Citation tokens: $2/1M, Reasoning tokens: $3/1M
            # Search: $5 per 1000 queries (handled separately)
        },
    },
}

# Default pricing for unknown models
DEFAULT_PRICING = {
    "input": 5.00,
    "output": 15.00,
}


@dataclass
class CostEstimate:
    """Cost estimate for a single API call."""
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    search_cost: float = 0.0
    total_cost: float = 0.0

    def __post_init__(self):
        self.total_cost = self.input_cost + self.output_cost + self.search_cost


class CostCalculator:
    """Calculate and track API costs."""

    def __init__(self):
        self.session_costs: list[CostEstimate] = []
        self.session_start = datetime.utcnow()
        self.warning_threshold = 5.00  # $5 warning

    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        search_sources: int = 0
    ) -> CostEstimate:
        """
        Calculate cost for a single API call.

        Args:
            provider: Provider name (anthropic, openai, google, xai)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            search_sources: Number of search sources used (for xAI)

        Returns:
            CostEstimate with breakdown
        """
        # Get pricing for this provider/model
        provider_pricing = PRICING.get(provider.lower(), {})
        model_pricing = provider_pricing.get(model, DEFAULT_PRICING)

        # Calculate token costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * model_pricing.get("input", DEFAULT_PRICING["input"])
        output_cost = (output_tokens / 1_000_000) * model_pricing.get("output", DEFAULT_PRICING["output"])

        # Calculate search costs (xAI specific)
        search_cost = 0.0
        if provider.lower() == "xai" and search_sources > 0:
            search_cost = search_sources * provider_pricing.get("search_cost_per_source", 0.025)

        estimate = CostEstimate(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            search_cost=search_cost
        )

        return estimate

    def add_to_session(self, estimate: CostEstimate):
        """Add a cost estimate to the session tracking."""
        self.session_costs.append(estimate)

    def get_session_total(self) -> float:
        """Get total cost for the current session."""
        return sum(e.total_cost for e in self.session_costs)

    def get_session_summary(self) -> Dict:
        """Get a summary of session costs by provider."""
        summary = {
            "total_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "query_count": len(self.session_costs),
            "by_provider": {},
            "session_start": self.session_start.isoformat(),
        }

        for estimate in self.session_costs:
            summary["total_cost"] += estimate.total_cost
            summary["total_input_tokens"] += estimate.input_tokens
            summary["total_output_tokens"] += estimate.output_tokens

            if estimate.provider not in summary["by_provider"]:
                summary["by_provider"][estimate.provider] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "queries": 0,
                }

            summary["by_provider"][estimate.provider]["cost"] += estimate.total_cost
            summary["by_provider"][estimate.provider]["input_tokens"] += estimate.input_tokens
            summary["by_provider"][estimate.provider]["output_tokens"] += estimate.output_tokens
            summary["by_provider"][estimate.provider]["queries"] += 1

        return summary

    def check_threshold_warning(self) -> Optional[str]:
        """Check if session cost exceeds warning threshold."""
        total = self.get_session_total()
        if total >= self.warning_threshold:
            return f"Session cost (${total:.2f}) has exceeded ${self.warning_threshold:.2f} threshold"
        return None

    def reset_session(self):
        """Reset session tracking."""
        self.session_costs = []
        self.session_start = datetime.utcnow()


def calculate_query_cost(results: Dict) -> Dict:
    """
    Calculate costs for a complete research query with multiple providers.

    Args:
        results: Dictionary of provider -> ResearchResult

    Returns:
        Dictionary with cost breakdown by provider and total
    """
    calculator = CostCalculator()
    costs = {
        "by_provider": {},
        "total": {
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
        }
    }

    for provider, result in results.items():
        if result.usage:
            # Handle both dict (OpenAI, Anthropic, xAI, Perplexity) and object (Google) usage formats
            if isinstance(result.usage, dict):
                input_tokens = result.usage.get("input_tokens", 0) or result.usage.get("prompt_tokens", 0) or 0
                output_tokens = result.usage.get("output_tokens", 0) or result.usage.get("completion_tokens", 0) or 0
            else:
                # Google returns usage_metadata as an object with attributes
                input_tokens = getattr(result.usage, 'prompt_token_count', 0) or getattr(result.usage, 'input_tokens', 0) or 0
                output_tokens = getattr(result.usage, 'candidates_token_count', 0) or getattr(result.usage, 'output_tokens', 0) or 0

            estimate = calculator.calculate_cost(
                provider=provider,
                model=result.model or "unknown",
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

            costs["by_provider"][provider] = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": estimate.input_cost,
                "output_cost": estimate.output_cost,
                "total_cost": estimate.total_cost,
                "model": result.model,
            }

            costs["total"]["input_tokens"] += input_tokens
            costs["total"]["output_tokens"] += output_tokens
            costs["total"]["cost"] += estimate.total_cost

    return costs


def format_cost_table(costs: Dict) -> str:
    """Format costs as a markdown table for display."""
    lines = []
    lines.append("| Provider | Model | Input | Output | Cost |")
    lines.append("|----------|-------|------:|-------:|-----:|")

    for provider, data in costs["by_provider"].items():
        model = data.get("model", "N/A")[:20]  # Truncate long model names
        input_tokens = f"{data['input_tokens']:,}"
        output_tokens = f"{data['output_tokens']:,}"
        cost = f"${data['total_cost']:.4f}"
        lines.append(f"| {provider.upper()} | {model} | {input_tokens} | {output_tokens} | {cost} |")

    # Total row
    total = costs["total"]
    lines.append(f"| **TOTAL** | - | **{total['input_tokens']:,}** | **{total['output_tokens']:,}** | **${total['cost']:.4f}** |")

    return "\n".join(lines)
