"""
xAI Grok Research Provider - Supports Grok 4 with DeepSearch via Agent Tools API.

DeepSearch uses server-side agentic execution that:
- Iteratively searches web and X (Twitter)
- Fires up to 10 RAG loops per prompt
- Pulls dozens of URLs and posts
- Reasons about conflicting information
- Returns comprehensive, cited responses

xAI's API is OpenAI-compatible, so we use the OpenAI SDK with a different base URL.
"""
from openai import OpenAI
from datetime import datetime
from typing import Optional
from .base_researcher import BaseResearcher, ResearchResult


class XAIResearcher(BaseResearcher):
    """xAI Grok research provider with basic and DeepSearch modes."""

    # Model configurations - Updated November 2025
    # grok-4-fast is recommended for agentic tool use
    BASIC_MODEL = "grok-4-0709"
    DEEP_RESEARCH_MODEL = "grok-4-fast"  # Best for DeepSearch agentic loops

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
        Run Grok DeepSearch using enhanced search_parameters.

        This provides comprehensive research by:
        - Using forced search mode with maximum results
        - Searching across web, news, and X sources
        - Enabling citations for source tracking
        - Using grok-4-fast for best agentic performance

        Note: The Agent Tools API (web_search/x_search tools) is being deprecated
        in favor of search_parameters. This implementation uses the stable API.
        """
        try:
            # Enhanced system prompt for deep research
            system_prompt = f"""You are Grok, conducting comprehensive deep competitive intelligence research on {company}.

Your task is to provide thorough, well-sourced analysis for defense technology competitive intelligence.

Research Guidelines:
1. Search the web extensively for current information, news, and official announcements
2. Search X (Twitter) for recent discussions, announcements, and industry sentiment
3. Cross-reference multiple sources to verify information
4. Look for SEC filings, press releases, contract awards, and government announcements
5. Search for industry analysis and trade publications
6. Provide specific dates, numbers, and facts
7. Cite every major claim with its source
8. Distinguish between verified facts and speculation

Synthesize findings into a comprehensive, well-cited report."""

            research_prompt = f"""Conduct comprehensive competitive intelligence research on {company}:

{prompt}

Be thorough. Search multiple sources including web, news, and X. Verify claims. Cite everything."""

            # Use search_parameters with maximum settings for deep research
            # Note: max_search_results must be <30, sources format is list of strings
            response = self.client.chat.completions.create(
                model=self.DEEP_RESEARCH_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": research_prompt
                    }
                ],
                extra_body={
                    "search_parameters": {
                        "mode": "on",  # Force search for deep research
                        "return_citations": True,
                        "max_search_results": 25  # Maximum is 30, use 25 for safety
                    }
                },
                temperature=0.3,
                max_tokens=16384  # Allow for longer deep research output
            )

            # Extract response text
            text = response.choices[0].message.content

            # Extract citations from response
            citations = []

            # Try model_extra first (where citations typically appear)
            if hasattr(response, 'model_extra') and response.model_extra:
                raw_citations = response.model_extra.get('citations', [])
                for url in raw_citations:
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]  # Domain as title
                    })

            # Also check choices for citations
            if hasattr(response.choices[0], 'message'):
                msg = response.choices[0].message
                if hasattr(msg, 'citations') and msg.citations:
                    for url in msg.citations:
                        if not any(c['url'] == url for c in citations):
                            citations.append({
                                "url": url,
                                "title": url.split('//')[-1].split('/')[0]
                            })

            return ResearchResult(
                provider=self.provider_name,
                model=self.DEEP_RESEARCH_MODEL,
                mode="deep",
                text=text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            )

        except Exception as e:
            # If deep research fails, fall back to basic with enhanced settings
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
