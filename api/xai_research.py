"""
xAI Grok Research Provider - Supports Grok 4.1 with DeepSearch via Responses API.

DeepSearch uses server-side agentic execution that:
- Iteratively searches web and X (Twitter)
- Fires up to 10 RAG loops per prompt
- Pulls dozens of URLs and posts
- Uses code execution for data analysis
- Reasons about conflicting information
- Returns comprehensive, cited responses

The Responses API provides:
- web_search: Real-time web search and page browsing
- x_search: Search X posts, users, and threads
- code_execution: Execute Python code for calculations

xAI's API is OpenAI-compatible, so we use the OpenAI SDK with a different base URL.
"""
from openai import OpenAI
from datetime import datetime
from typing import Optional
import requests
from .base_researcher import BaseResearcher, ResearchResult


class XAIResearcher(BaseResearcher):
    """xAI Grok research provider with basic and DeepSearch modes."""

    # Model configurations - Updated December 2025
    BASIC_MODEL = "grok-4-0709"
    # grok-4.1-fast: Best for agentic tool use, state-of-the-art web/X search
    DEEP_RESEARCH_MODEL = "grok-4.1-fast"

    # xAI API base URL
    BASE_URL = "https://api.x.ai/v1"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "xai"
        # xAI uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL
        )

    def basic_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run Grok query WITH web search (always enabled).
        Uses search_parameters for real-time web and X search access.
        """
        try:
            system_prompt = f"""You are Grok, conducting competitive intelligence research on {company}.

Use web search and X search to find current, verified information:
1. Search the web for recent news and announcements
2. Search X for industry discussions and updates
3. Cite your sources

Provide well-structured analysis."""

            response = self.client.chat.completions.create(
                model=self.BASIC_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                extra_body={
                    "search_parameters": {
                        "mode": "auto",  # Let Grok decide when to search
                        "return_citations": True,
                        "max_search_results": 10
                    }
                },
                temperature=0.3,
                max_tokens=8192
            )

            # Extract citations from response.model_extra['citations']
            citations = []
            if hasattr(response, 'model_extra') and response.model_extra:
                raw_citations = response.model_extra.get('citations', [])
                for url in raw_citations:
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]  # Domain as title
                    })

            return ResearchResult(
                provider=self.provider_name,
                model=self.BASIC_MODEL,
                mode="basic",
                text=response.choices[0].message.content,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            )

        except Exception as e:
            return self._create_error_result(str(e), "basic")

    def deep_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run Grok DeepSearch using the Responses API with Agent Tools.

        This is the SAME DeepSearch capability as grok.com, providing:
        - web_search: Real-time web search and page browsing
        - x_search: Search X posts, users, and threads
        - code_execution: Python execution for data analysis
        - Iterative RAG loops (up to 10 per prompt)

        The model autonomously decides when and what to search.
        """
        try:
            # Use the Responses API endpoint for agentic deep research
            # This mirrors the DeepSearch experience on grok.com
            response = self.client.responses.create(
                model=self.DEEP_RESEARCH_MODEL,
                input=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": f"""You are Grok, conducting comprehensive deep competitive intelligence research on {company} for defense technology analysis.

Your goal is to produce a thorough, well-sourced intelligence report that covers:
- Recent developments and news (last 30-90 days)
- Financial data, contracts, and SEC filings
- Strategic direction and competitive positioning
- Technology capabilities and investments
- Leadership and organizational changes
- Industry sentiment and expert opinions

Use web search extensively to find current information. Use X search to find industry discussions, announcements, and sentiment. Cross-reference claims across multiple sources. Be thorough and verify everything."""
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": f"""Conduct comprehensive competitive intelligence research on {company}:

{prompt}

Provide a detailed report with:
1. Executive summary of key findings
2. Detailed analysis organized by topic
3. Specific dates, numbers, and citations
4. Analysis of implications for competitive positioning
5. Areas of uncertainty or conflicting information

Search both the web and X to gather comprehensive information."""
                            }
                        ]
                    }
                ],
                tools=[
                    {"type": "web_search"},  # Real-time web search
                    {"type": "x_search"}     # Search X posts and threads
                ]
            )

            # Extract text from the response
            text = ""
            if hasattr(response, 'output') and response.output:
                for output_block in response.output:
                    if hasattr(output_block, 'content'):
                        for content_item in output_block.content:
                            if hasattr(content_item, 'text'):
                                text += content_item.text

            # Fallback to output_text
            if not text and hasattr(response, 'output_text'):
                text = response.output_text

            # Extract citations from tool results
            citations = []
            seen_urls = set()
            if hasattr(response, 'output') and response.output:
                for output_block in response.output:
                    # Check for web_search results
                    if hasattr(output_block, 'type') and output_block.type in ['web_search_result', 'x_search_result']:
                        if hasattr(output_block, 'results'):
                            for result in output_block.results:
                                url = getattr(result, 'url', None)
                                if url and url not in seen_urls:
                                    seen_urls.add(url)
                                    citations.append({
                                        "url": url,
                                        "title": getattr(result, 'title', url.split('//')[-1].split('/')[0])
                                    })
                    # Check for annotations in content
                    if hasattr(output_block, 'content'):
                        for content_item in output_block.content:
                            if hasattr(content_item, 'annotations'):
                                for annotation in content_item.annotations:
                                    url = getattr(annotation, 'url', None)
                                    if url and url not in seen_urls:
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
            # If Responses API fails, fall back to search_parameters approach
            return self._deep_research_fallback(prompt, company, str(e))

    def _deep_research_fallback(self, prompt: str, company: str, original_error: str) -> ResearchResult:
        """
        Fallback to search_parameters if Agent Tools API is not available.
        Uses forced search mode with maximum results.
        """
        try:
            system_prompt = f"""You are Grok, conducting deep competitive intelligence research on {company}.

Use DeepSearch to thoroughly investigate:
1. Search the web for current information, news, and official announcements
2. Search X (Twitter) for recent discussions, announcements, and industry sentiment
3. Cross-reference multiple sources to verify information
4. Synthesize findings into a comprehensive, well-cited report

Be thorough, cite your sources, and distinguish between verified facts and speculation."""

            response = self.client.chat.completions.create(
                model=self.BASIC_MODEL,  # Fall back to stable model
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                extra_body={
                    "search_parameters": {
                        "mode": "on",  # Force search for deep research
                        "return_citations": True,
                        "max_search_results": 50,  # Maximum results
                        "sources": ["web", "news", "x"]  # Search all sources
                    }
                },
                temperature=0.3,
                max_tokens=16384
            )

            # Extract citations from response.model_extra['citations']
            citations = []
            if hasattr(response, 'model_extra') and response.model_extra:
                raw_citations = response.model_extra.get('citations', [])
                for url in raw_citations:
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]  # Domain as title
                    })

            return ResearchResult(
                provider=self.provider_name,
                model=self.BASIC_MODEL,
                mode="deep",
                text=response.choices[0].message.content,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            )

        except Exception as e:
            return self._create_error_result(f"DeepSearch failed: {original_error}. Fallback also failed: {str(e)}", "deep")
