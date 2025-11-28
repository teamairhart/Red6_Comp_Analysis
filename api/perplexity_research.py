"""
Perplexity Research Provider - Supports Sonar Pro and Sonar Deep Research.

Perplexity's API is OpenAI-compatible, providing:
- sonar-pro: Real-time web-connected research with multi-step reasoning
- sonar-deep-research: Exhaustive research across hundreds of sources

All Sonar models include built-in web search - no separate search tool needed.
Citations are returned as URLs in the response.
"""
import requests
from datetime import datetime
from typing import Optional, List
from .base_researcher import BaseResearcher, ResearchResult


class PerplexityResearcher(BaseResearcher):
    """Perplexity research provider with basic (sonar-pro) and deep (sonar-deep-research) modes."""

    # Model configurations - November 2025
    # sonar-pro: Best for real-time research with web search
    # sonar-deep-research: Exhaustive multi-query research
    BASIC_MODEL = "sonar-pro"
    DEEP_RESEARCH_MODEL = "sonar-deep-research"

    # API endpoint
    BASE_URL = "https://api.perplexity.ai/chat/completions"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "perplexity"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def basic_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run Sonar Pro query with real-time web search.

        Sonar Pro provides:
        - Multi-step reasoning for complex queries
        - Real-time web search integration
        - 2x more citations than standard Sonar
        - Search recency filtering for recent results
        """
        try:
            system_prompt = f"""You are a competitive intelligence analyst conducting research on {company} for defense technology analysis.

Search the web to find current, verified information. Focus on:
1. Recent news and announcements
2. Official company sources and press releases
3. Industry publications and analysis
4. Financial data and SEC filings

Provide well-structured analysis with sources cited."""

            payload = {
                "model": self.BASIC_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 8192,
                "web_search_options": {
                    "search_recency_filter": "month"  # Focus on recent results
                }
            }

            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=120  # 2 minute timeout for basic research
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from response
            text = ""
            if data.get("choices") and len(data["choices"]) > 0:
                text = data["choices"][0].get("message", {}).get("content", "")

            # Extract citations - Perplexity returns URLs in a 'citations' array
            citations = []
            if data.get("citations"):
                for url in data["citations"]:
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]  # Domain as title
                    })

            # Extract usage
            usage = None
            if data.get("usage"):
                usage = {
                    "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                    "completion_tokens": data["usage"].get("completion_tokens", 0),
                    "total_tokens": data["usage"].get("total_tokens", 0)
                }

            return ResearchResult(
                provider=self.provider_name,
                model=self.BASIC_MODEL,
                mode="basic",
                text=text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage=usage
            )

        except requests.exceptions.RequestException as e:
            return self._create_error_result(f"Request failed: {str(e)}", "basic")
        except Exception as e:
            return self._create_error_result(str(e), "basic")

    def deep_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run Sonar Deep Research for exhaustive multi-source analysis.

        Deep Research provides:
        - Autonomous research across hundreds of sources
        - Multi-query research threads (up to 21+ search queries)
        - Expert-level synthesis and insights
        - Comprehensive source-rich reports
        - Extended reasoning for complex analysis

        Note: Deep research can take 1-3+ minutes to complete.
        """
        try:
            # Deep research prompt - encourage thorough investigation
            system_prompt = f"""You are conducting comprehensive deep competitive intelligence research on {company} for defense technology analysis.

Your task is to provide thorough, well-sourced analysis using exhaustive web research.

RESEARCH METHODOLOGY:
1. INITIAL DISCOVERY: Search for recent news, press releases, and official announcements
2. VERIFICATION: Cross-reference claims with multiple sources
3. DEEP DIVE: Search for specific topics - contracts, partnerships, financials, leadership
4. INDUSTRY CONTEXT: Search for industry analysis and competitive positioning
5. SYNTHESIS: Combine findings into a comprehensive report

QUALITY STANDARDS:
- Verify claims with multiple sources
- Cite specific sources with dates
- Note when information is uncertain or conflicting
- Distinguish between verified facts and speculation
- Include specific numbers, dates, and financial figures

Be thorough and comprehensive. Use extensive research to verify each major claim."""

            research_prompt = f"""Conduct comprehensive competitive intelligence research on {company}:

{prompt}

REQUIREMENTS:
1. Search multiple sources to verify each major claim
2. Provide specific dates, numbers, and facts
3. Cite all sources
4. Note any conflicting information found
5. Distinguish between confirmed facts and speculation

Be exhaustive in your research."""

            payload = {
                "model": self.DEEP_RESEARCH_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": research_prompt
                    }
                ]
                # Note: Deep research model handles its own parameters
            }

            # Deep research can take several minutes
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=600  # 10 minute timeout for deep research
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from response
            text = ""
            if data.get("choices") and len(data["choices"]) > 0:
                text = data["choices"][0].get("message", {}).get("content", "")

            # Extract citations
            citations = []
            if data.get("citations"):
                for url in data["citations"]:
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]
                    })

            # Extract usage - deep research has additional fields
            usage = None
            if data.get("usage"):
                usage = {
                    "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                    "completion_tokens": data["usage"].get("completion_tokens", 0),
                    "total_tokens": data["usage"].get("total_tokens", 0),
                    "citation_tokens": data["usage"].get("citation_tokens", 0),
                    "num_search_queries": data["usage"].get("num_search_queries", 0),
                    "reasoning_tokens": data["usage"].get("reasoning_tokens", 0)
                }

            return ResearchResult(
                provider=self.provider_name,
                model=self.DEEP_RESEARCH_MODEL,
                mode="deep",
                text=text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage=usage
            )

        except requests.exceptions.Timeout:
            return self._create_error_result(
                "Deep research timed out after 10 minutes. The query may be too complex.",
                "deep"
            )
        except requests.exceptions.RequestException as e:
            return self._create_error_result(f"Request failed: {str(e)}", "deep")
        except Exception as e:
            return self._create_error_result(str(e), "deep")
