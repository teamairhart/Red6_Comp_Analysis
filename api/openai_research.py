"""
OpenAI Research Provider - Supports GPT-5.1 with web search via Responses API.

Uses the Responses API which provides built-in web search capabilities.
For deep research, we use enhanced prompting with GPT-5.1 to get comprehensive results.
"""
from openai import OpenAI
from datetime import datetime
from typing import Optional
import time
from .base_researcher import BaseResearcher, ResearchResult


class OpenAIResearcher(BaseResearcher):
    """OpenAI research provider with basic and deep research modes."""

    # Model configurations - Updated November 2025
    BASIC_MODEL = "gpt-5.1"

    # For deep research, we use GPT-5.1 with enhanced prompting
    # The o3-deep-research models require special access
    DEEP_RESEARCH_MODEL = "gpt-5.1"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "openai"
        self.client = OpenAI(api_key=api_key)

    def basic_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run GPT-5.1 query WITH web search (always enabled).
        Uses the responses API with web_search_preview tool.
        """
        try:
            full_prompt = f"""You are a competitive intelligence analyst conducting research on {company}.
Search the web to find current, verified information. Cite your sources.

RESEARCH REQUEST:
{prompt}"""

            # Use responses API with web_search_preview tool
            response = self.client.responses.create(
                model=self.BASIC_MODEL,
                tools=[{"type": "web_search_preview"}],
                input=full_prompt
            )

            # Extract text from response
            text = response.output_text if hasattr(response, 'output_text') else ""

            # Extract citations from output if available
            citations = []
            if hasattr(response, 'output') and response.output:
                for output_block in response.output:
                    if hasattr(output_block, 'content'):
                        for content_item in output_block.content:
                            if hasattr(content_item, 'annotations'):
                                for annotation in content_item.annotations:
                                    if hasattr(annotation, 'url'):
                                        citations.append({
                                            "url": annotation.url,
                                            "title": getattr(annotation, 'title', annotation.url)
                                        })

            return ResearchResult(
                provider=self.provider_name,
                model=self.BASIC_MODEL,
                mode="basic",
                text=text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage=getattr(response, 'usage', None)
            )

        except Exception as e:
            return self._create_error_result(str(e), "basic")

    def deep_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run OpenAI Deep Research using GPT-5.1 with enhanced prompting.

        Uses the Responses API with web_search_preview tool and comprehensive
        prompting to guide thorough research. GPT-5.1 provides excellent
        research capabilities with web search.
        """
        try:
            # Comprehensive research prompt
            full_prompt = f"""You are a competitive intelligence analyst conducting comprehensive deep research on {company} for defense technology competitive intelligence.

RESEARCH TASK:
{prompt}

RESEARCH METHODOLOGY - Follow these steps:
1. INITIAL DISCOVERY: Search for recent news, press releases, and official announcements about {company}
2. VERIFICATION: Cross-reference major claims with multiple sources
3. FINANCIAL DATA: Search for SEC filings, earnings reports, contract awards, and government announcements
4. INDUSTRY CONTEXT: Search for industry analysis, competitive positioning, and trade publications
5. RECENT DEVELOPMENTS: Focus on the last 30-90 days for the most current information

QUALITY STANDARDS:
- For every major claim or data point, verify with search
- Cite specific sources with dates when available
- Note when information is uncertain or conflicting
- Distinguish between verified facts and speculation
- Include specific numbers, dates, and financial figures

OUTPUT FORMAT:
- Provide a comprehensive, well-structured report
- Use clear sections and headings
- Include inline citations for key facts
- End with a summary of key findings

Be thorough and comprehensive. Search multiple sources to verify each major claim."""

            response = self.client.responses.create(
                model=self.DEEP_RESEARCH_MODEL,
                tools=[{"type": "web_search_preview"}],
                input=full_prompt
            )

            # Extract text from response
            text = response.output_text if hasattr(response, 'output_text') else ""

            # Extract citations from output if available
            citations = []
            if hasattr(response, 'output') and response.output:
                for output_block in response.output:
                    if hasattr(output_block, 'content'):
                        for content_item in output_block.content:
                            if hasattr(content_item, 'annotations'):
                                for annotation in content_item.annotations:
                                    if hasattr(annotation, 'url'):
                                        citations.append({
                                            "url": annotation.url,
                                            "title": getattr(annotation, 'title', annotation.url)
                                        })

            return ResearchResult(
                provider=self.provider_name,
                model=self.DEEP_RESEARCH_MODEL,
                mode="deep",
                text=text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage=getattr(response, 'usage', None)
            )

        except Exception as e:
            return self._create_error_result(str(e), "deep")
