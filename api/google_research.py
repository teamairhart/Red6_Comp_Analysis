"""
Google Gemini Research Provider - Supports Gemini 3 Pro with Google Search Grounding.

Gemini 3 Pro (gemini-3-pro-preview) launched November 2025 provides:
- 1M token context window for comprehensive research
- Real-time Google Search integration with grounding
- Grounding metadata with source URLs and titles
- Extended thinking with thinking_level parameter
- Advanced reasoning capabilities

Note: Full Deep Research API via Discovery Engine requires allowlist access.
This implementation uses Gemini with Google Search grounding for real-time research.
"""
from datetime import datetime
from typing import Optional
from .base_researcher import BaseResearcher, ResearchResult

# Google GenAI import
try:
    from google import genai
    from google.genai.types import GenerateContentConfig, GoogleSearch, Tool
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleResearcher(BaseResearcher):
    """Google Gemini research provider with basic and grounded search modes."""

    # Model configurations - Updated December 2025
    # gemini-3-pro-preview: Most advanced Gemini model with 1M context, reasoning, grounding
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
        Run Gemini Deep Research using multi-phase approach with Google Search grounding.

        This implements comprehensive research through:
        - Phase 1: Initial discovery with broad Google Search
        - Phase 2: Deep dive and verification with targeted searches
        - Extended thinking for complex analysis
        - Multiple search queries executed per phase

        Note: Full Discovery Engine Deep Research API requires allowlist access.
        This approach provides similar depth using grounded search.
        """
        return self._multi_phase_research(prompt, company)

    def _multi_phase_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Multi-phase research approach for comprehensive coverage.
        """
        try:
            all_citations = []
            all_text_parts = []
            seen_urls = set()

            # Phase 1: Initial discovery
            phase1_prompt = f"""PHASE 1 - INITIAL DISCOVERY for {company}:

{prompt}

Focus on discovering:
- Recent news and announcements (last 30-90 days)
- Key developments and milestones
- Official company statements and press releases
- Major contracts and partnerships

Use Google Search to find current information. Cite all sources.
Note any areas that need deeper investigation."""

            phase1_response = self.client.models.generate_content(
                model=self.DEEP_RESEARCH_MODEL,
                contents=phase1_prompt,
                config={
                    "temperature": 0.3,
                    "max_output_tokens": 8192,
                    "tools": [{"google_search": {}}],
                    "thinking_config": {
                        "thinking_level": "high"  # Max reasoning for research
                    }
                }
            )

            phase1_text = phase1_response.text if hasattr(phase1_response, 'text') else ""
            phase1_citations = self._extract_citations(phase1_response, seen_urls)
            all_text_parts.append("## Phase 1: Initial Discovery\n\n" + phase1_text)
            all_citations.extend(phase1_citations)

            # Phase 2: Deep dive and verification
            phase2_prompt = f"""PHASE 2 - VERIFICATION AND DEEP DIVE for {company}:

Based on initial findings, now conduct deeper research:

INITIAL FINDINGS SUMMARY:
{phase1_text[:3000]}

Your task:
1. Cross-reference and verify key claims with additional sources
2. Search for more specific details on important topics
3. Look for financial data, SEC filings, and official documents
4. Find industry analysis and expert commentary
5. Note any conflicting information

Be thorough. Cite all sources. Provide specific dates and numbers."""

            phase2_response = self.client.models.generate_content(
                model=self.DEEP_RESEARCH_MODEL,
                contents=phase2_prompt,
                config={
                    "temperature": 0.3,
                    "max_output_tokens": 12000,
                    "tools": [{"google_search": {}}],
                    "thinking_config": {
                        "thinking_level": "high"  # Max reasoning for verification
                    }
                }
            )

            phase2_text = phase2_response.text if hasattr(phase2_response, 'text') else ""
            phase2_citations = self._extract_citations(phase2_response, seen_urls)
            all_text_parts.append("\n\n## Phase 2: Verification & Deep Dive\n\n" + phase2_text)
            all_citations.extend(phase2_citations)

            return ResearchResult(
                provider=self.provider_name,
                model=self.DEEP_RESEARCH_MODEL,
                mode="deep",
                text="\n".join(all_text_parts),
                citations=all_citations,
                timestamp=datetime.utcnow(),
                usage=None  # Combined usage not easily tracked
            )

        except Exception as e:
            return self._create_error_result(str(e), "deep")

    def _extract_citations(self, response, seen_urls: set) -> list:
        """Extract citations from Gemini response grounding metadata."""
        citations = []

        # Try grounding_metadata on response
        if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
            grounding = response.grounding_metadata
            if hasattr(grounding, 'grounding_chunks'):
                for chunk in grounding.grounding_chunks:
                    if hasattr(chunk, 'web'):
                        url = chunk.web.uri
                        if url not in seen_urls:
                            seen_urls.add(url)
                            citations.append({
                                "url": url,
                                "title": getattr(chunk.web, 'title', '')
                            })

        # Try candidate-level grounding_metadata (Gemini 3+)
        if hasattr(response, 'candidates') and response.candidates:
            cand = response.candidates[0]
            if hasattr(cand, 'grounding_metadata') and cand.grounding_metadata:
                gm = cand.grounding_metadata
                if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                    for chunk in gm.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            url = chunk.web.uri
                            if url not in seen_urls:
                                seen_urls.add(url)
                                citations.append({
                                    "url": url,
                                    "title": getattr(chunk.web, 'title', '')
                                })

        # Fallback: extract URLs from response text
        if not citations and hasattr(response, 'text') and response.text:
            import re
            url_pattern = r'https?://[^\s\)\]\>\"\']+[^\s\)\]\>\"\'\.\,]'
            found_urls = re.findall(url_pattern, response.text)
            for url in found_urls[:20]:
                if url not in seen_urls:
                    seen_urls.add(url)
                    citations.append({
                        "url": url,
                        "title": url.split('//')[-1].split('/')[0]
                    })

        return citations

    def _single_phase_deep_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Alternative: Single-phase deep research with extended thinking.
        Faster but less thorough than multi-phase approach.
        """
        try:
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
                        "thinking_level": "high"  # Max reasoning for comprehensive research
                    }
                }
            )

            seen_urls = set()
            citations = self._extract_citations(response, seen_urls)

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
