# Competitive Analysis Research - API Modules
"""
This package contains API modules for each LLM provider,
supporting both basic and deep research modes.
"""

from .openai_research import OpenAIResearcher
from .anthropic_research import AnthropicResearcher
from .google_research import GoogleResearcher
from .xai_research import XAIResearcher
from .research_engine import ResearchEngine
from .synthesis_agent import SynthesisAgent, SynthesisResult, format_synthesis_report, save_synthesis_report
from .export_utils import ReportExporter, export_report

__all__ = [
    "OpenAIResearcher",
    "AnthropicResearcher",
    "GoogleResearcher",
    "XAIResearcher",
    "ResearchEngine",
    "SynthesisAgent",
    "SynthesisResult",
    "format_synthesis_report",
    "save_synthesis_report",
    "ReportExporter",
    "export_report"
]
