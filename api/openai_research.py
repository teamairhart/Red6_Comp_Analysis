"""
OpenAI Research Provider - Supports GPT-5.1 and Deep Research API.

Uses the Responses API which provides built-in web search capabilities.
For deep research, we use the dedicated o3-deep-research model which provides
agentic multi-step research with web search and code interpreter.
"""
from openai import OpenAI
from datetime import datetime
from typing import Optional
import time
from .base_researcher import BaseResearcher, ResearchResult


class OpenAIResearcher(BaseResearcher):
    """OpenAI research provider with basic and deep research modes."""

    # Model configurations - Updated December 2025
    BASIC_MODEL = "gpt-5.1"

    # Deep Research models - launched June 27, 2025
    # o3-deep-research: Optimized for in-depth synthesis and higher-quality output
    # o4-mini-deep-research: Lightweight and faster, ideal for latency-sensitive use cases
    DEEP_RESEARCH_MODEL = "o3-deep-research-2025-06-26"

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
        Run OpenAI Deep Research using the dedicated o3-deep-research model.

        This is the SAME Deep Research capability as ChatGPT's Deep Research feature.
        The model autonomously:
        - Plans sub-questions and research strategy
        - Searches the web multiple times
        - Synthesizes findings across sources
        - Produces a comprehensive structured report

        Note: Deep research can take several minutes to complete.
        """
        try:
            # System message for competitive intelligence context
            system_message = f"""You are a competitive intelligence analyst conducting comprehensive deep research on {company} for defense technology analysis.

Your goal is to produce a thorough, well-sourced intelligence report that covers:
- Recent developments (last 30-90 days)
- Financial and contract data
- Strategic direction and competitive positioning
- Technology capabilities and investments
- Leadership and organizational changes

Be thorough and verify claims with multiple sources."""

            # User query with the research prompt
            user_query = f"""Conduct comprehensive competitive intelligence research on {company}:

{prompt}

Provide a detailed report with:
1. Executive summary
2. Key findings organized by topic
3. Specific dates, numbers, and citations
4. Analysis of implications
5. Areas of uncertainty or conflicting information"""

            # Use the o3-deep-research model with the Responses API
            # This model expects the specific input format from the OpenAI Deep Research API
            response = self.client.responses.create(
                model=self.DEEP_RESEARCH_MODEL,
                input=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": system_message
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": user_query
                            }
                        ]
                    }
                ],
                reasoning={
                    "summary": "auto"  # Let the model decide on summary detail level
                },
                tools=[
                    {"type": "web_search_preview"}
                ]
            )

            # Extract text from the final output
            text = ""
            if hasattr(response, 'output') and response.output:
                # Get the last output block which contains the final report
                for output_block in response.output:
                    if hasattr(output_block, 'content'):
                        for content_item in output_block.content:
                            if hasattr(content_item, 'text'):
                                text += content_item.text

            # Fallback to output_text if available
            if not text and hasattr(response, 'output_text'):
                text = response.output_text

            # Extract citations from annotations in the output
            citations = []
            seen_urls = set()
            if hasattr(response, 'output') and response.output:
                for output_block in response.output:
                    if hasattr(output_block, 'content'):
                        for content_item in output_block.content:
                            if hasattr(content_item, 'annotations'):
                                for annotation in content_item.annotations:
                                    if hasattr(annotation, 'url'):
                                        url = annotation.url
                                        if url not in seen_urls:
                                            seen_urls.add(url)
                                            citations.append({
                                                "url": url,
                                                "title": getattr(annotation, 'title', url)
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
