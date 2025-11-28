"""
Google Gemini Research Provider - Supports Gemini 3 Pro with Grounding.

Note: Full Deep Research API requires allowlist access via Discovery Engine.
This implementation uses Gemini with Google Search grounding as the available alternative.
"""
from datetime import datetime
from typing import Optional
from .base_researcher import BaseResearcher, ResearchResult

# Google GenAI import
try:
    from google import genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleResearcher(BaseResearcher):
    """Google Gemini research provider with basic and grounded search modes."""

    # Model configurations - Updated November 2025
    BASIC_MODEL = "gemini-3-pro-preview"
    DEEP_RESEARCH_MODEL = "gemini-3-pro-preview"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "google"

        if not GOOGLE_AVAILABLE:
            raise ImportError("google-genai package not installed. Run: pip install google-genai")

        self.client = genai.Client(api_key=api_key)

    def basic_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run Gemini query WITH Google Search grounding (always enabled).
        Basic mode uses search grounding for current information.
        """
        try:
            research_prompt = f"""You are a competitive intelligence analyst conducting research on {company}.

Use Google Search to find current, verified information. Search for:
1. Recent news and announcements
2. Official company sources
3. Industry publications

Cite your sources.

RESEARCH REQUEST:
{prompt}"""

            response = self.client.models.generate_content(
                model=self.BASIC_MODEL,
                contents=research_prompt,
                config={
                    "temperature": 0.3,
                    "max_output_tokens": 8192,
                    "tools": [{"google_search": {}}]  # Always enable search
                }
            )

            # Extract citations from grounding metadata (if available)
            citations = []

            # Try grounding_metadata on response
            if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                grounding = response.grounding_metadata
                if hasattr(grounding, 'grounding_chunks'):
                    for chunk in grounding.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            citations.append({
                                "url": chunk.web.uri,
                                "title": chunk.web.title
                            })

            # Try candidate-level grounding_metadata (Gemini 3+)
            if not citations and hasattr(response, 'candidates') and response.candidates:
                cand = response.candidates[0]
                if hasattr(cand, 'grounding_metadata') and cand.grounding_metadata:
                    gm = cand.grounding_metadata
                    if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                        for chunk in gm.grounding_chunks:
                            if hasattr(chunk, 'web'):
                                citations.append({
                                    "url": chunk.web.uri,
                                    "title": getattr(chunk.web, 'title', '')
                                })

            # Fallback: extract URLs from response text
            if not citations and response.text:
                import re
                url_pattern = r'https?://[^\s\)\]\>\"\']+[^\s\)\]\>\"\'\.\,]'
                found_urls = re.findall(url_pattern, response.text)
                for url in found_urls[:20]:  # Limit to 20
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]  # Domain as title
                    })

            return ResearchResult(
                provider=self.provider_name,
                model=self.BASIC_MODEL,
                mode="basic",
                text=response.text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage=getattr(response, 'usage_metadata', None)
            )

        except Exception as e:
            return self._create_error_result(str(e), "basic")

    def deep_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Run Gemini Deep Research query with Google Search grounding.

        Note: This uses Google Search grounding as the available API option.
        Full Deep Research via Discovery Engine requires allowlist access.
        """
        try:
            # Enhanced prompt for deep research
            research_prompt = f"""You are conducting deep competitive intelligence research on {company}.

Use Google Search grounding extensively to find and verify:
1. Current information from official sources
2. Recent news and press releases
3. SEC filings and financial data
4. Contract awards and government announcements
5. Industry analysis and trade publications

For every major claim, provide the source. Be thorough and comprehensive.

RESEARCH REQUEST:
{prompt}"""

            response = self.client.models.generate_content(
                model=self.DEEP_RESEARCH_MODEL,
                contents=research_prompt,
                config={
                    "temperature": 0.3,
                    "max_output_tokens": 16384,
                    "tools": [{"google_search": {}}],
                    "thinking_config": {
                        "thinking_budget": 10000  # Enable extended thinking
                    }
                }
            )

            # Extract citations from grounding metadata (if available)
            citations = []

            # Try grounding_metadata on response
            if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                grounding = response.grounding_metadata
                if hasattr(grounding, 'grounding_chunks'):
                    for chunk in grounding.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            citations.append({
                                "url": chunk.web.uri,
                                "title": chunk.web.title
                            })

            # Try candidate-level grounding_metadata (Gemini 3+)
            if not citations and hasattr(response, 'candidates') and response.candidates:
                cand = response.candidates[0]
                if hasattr(cand, 'grounding_metadata') and cand.grounding_metadata:
                    gm = cand.grounding_metadata
                    if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                        for chunk in gm.grounding_chunks:
                            if hasattr(chunk, 'web'):
                                citations.append({
                                    "url": chunk.web.uri,
                                    "title": getattr(chunk.web, 'title', '')
                                })

            # Fallback: extract URLs from response text
            if not citations and response.text:
                import re
                url_pattern = r'https?://[^\s\)\]\>\"\']+[^\s\)\]\>\"\'\.\,]'
                found_urls = re.findall(url_pattern, response.text)
                for url in found_urls[:20]:  # Limit to 20
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]  # Domain as title
                    })

            return ResearchResult(
                provider=self.provider_name,
                model=self.DEEP_RESEARCH_MODEL,
                mode="deep",
                text=response.text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage=getattr(response, 'usage_metadata', None)
            )

        except Exception as e:
            return self._create_error_result(str(e), "deep")


class GoogleDeepResearchClient:
    """
    Client for Google's full Deep Research API via Discovery Engine.

    NOTE: This requires:
    1. Google Cloud Project with Discovery Engine API enabled
    2. Allowlist approval from Google
    3. Proper authentication via service account

    This class is provided for future use when allowlist access is granted.
    """

    def __init__(self, project_id: str, app_id: str, credentials_path: str = None):
        self.project_id = project_id
        self.app_id = app_id
        self.endpoint = (
            f"https://discoveryengine.googleapis.com/v1/projects/{project_id}"
            f"/locations/global/collections/default_collection"
            f"/engines/{app_id}/assistants/default_assistant:streamAssist"
        )

    def research(self, query: str) -> dict:
        """
        Run full Deep Research query via Discovery Engine.

        This is a placeholder - implementation requires:
        - Google Cloud authentication
        - Discovery Engine API access
        - Allowlist approval

        Returns:
            Streaming response with research plan, progress, and final report
        """
        raise NotImplementedError(
            "Full Deep Research API requires Discovery Engine allowlist access. "
            "Use GoogleResearcher.deep_research() for grounded search instead."
        )
