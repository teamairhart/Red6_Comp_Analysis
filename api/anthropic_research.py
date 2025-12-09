"""
Anthropic Research Provider - Supports Claude Opus 4.5 with Web Search.

Claude's web search tool (web_search_20250305) handles agentic searching internally,
deciding when and how to search based on the query. For deep research, we:
1. Increase max_uses to allow more searches
2. Use enhanced prompting to encourage thorough research
3. Implement a multi-phase approach for comprehensive coverage
"""
import anthropic
from datetime import datetime
from typing import Optional, List
from .base_researcher import BaseResearcher, ResearchResult


class AnthropicResearcher(BaseResearcher):
    """Anthropic Claude research provider with basic and deep research modes."""

    # Model configurations - Claude Opus 4.5 is the best for research
    BASIC_MODEL = "claude-opus-4-5-20251101"
    DEEP_RESEARCH_MODEL = "claude-opus-4-5-20251101"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "anthropic"
        self.client = anthropic.Anthropic(api_key=api_key)

    def basic_research(self, prompt: str, company: str, max_searches: int = 5) -> ResearchResult:
        """
        Run basic Claude query WITH web search (always enabled).
        Basic mode uses fewer searches for faster, more focused results.
        """
        try:
            system_prompt = f"""You are a competitive intelligence analyst conducting research on {company} for defense technology analysis.

You have access to web search - USE IT to find current, verified information. Search for:
1. Recent news and announcements
2. Official company sources
3. Industry publications

Provide well-structured analysis with sources cited."""

            response = self.client.messages.create(
                model=self.BASIC_MODEL,
                max_tokens=8192,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                system=system_prompt,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": max_searches  # Fewer searches for basic mode
                }]
            )

            # Extract text and citations from response
            text, citations = self._extract_response_content(response)

            return ResearchResult(
                provider=self.provider_name,
                model=self.BASIC_MODEL,
                mode="basic",
                text=text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )

        except Exception as e:
            return self._create_error_result(str(e), "basic")

    def deep_research(self, prompt: str, company: str, max_searches: int = 20) -> ResearchResult:
        """
        Run Claude Deep Research using multi-phase agentic approach.

        This mirrors the Research mode in Claude.ai which can research for up to 45 minutes.
        We implement a two-phase approach:
        - Phase 1: Initial discovery and broad research (15 searches)
        - Phase 2: Verification, deep dive, and synthesis (15 searches)

        Total: 30 web searches across two research phases for comprehensive coverage.
        """
        # Use multi-phase research for true deep research capability
        return self.multi_phase_research(prompt, company)

    def _single_phase_deep_research(self, prompt: str, company: str, max_searches: int = 20) -> ResearchResult:
        """
        Alternative: Single-phase deep research with high search count.
        Faster but less thorough than multi-phase approach.
        """
        try:
            # Enhanced system prompt for deep research
            system_prompt = f"""You are a competitive intelligence analyst conducting comprehensive deep research on {company} for defense technology analysis.

Your task is to provide thorough, well-sourced analysis. You have access to web search - USE IT EXTENSIVELY.

RESEARCH METHODOLOGY:
1. INITIAL DISCOVERY: Search for recent news, press releases, and official announcements
2. VERIFICATION: Cross-reference claims with multiple sources
3. DEEP DIVE: Search for specific topics mentioned in the research prompt
4. FINANCIAL DATA: Look for SEC filings, earnings reports, contract awards
5. INDUSTRY CONTEXT: Search for industry analysis and competitive positioning

QUALITY STANDARDS:
- For every major claim or data point, search to verify
- Cite specific sources with dates when available
- Note when information is uncertain or conflicting
- Distinguish between verified facts and speculation
- Include specific numbers, dates, and financial figures when available

You have up to {max_searches} web searches available - use them to be thorough."""

            research_prompt = f"""Conduct comprehensive competitive intelligence research on {company}:

{prompt}

REQUIREMENTS:
1. Search multiple sources to verify each major claim
2. Provide specific dates, numbers, and facts
3. Cite all sources
4. Note any conflicting information found
5. Distinguish between confirmed facts and speculation

Be thorough and comprehensive. Use all available searches if needed."""

            # Use streaming to handle long-running operations (>10 min timeout)
            text = ""
            citations = []
            seen_urls = set()
            input_tokens = 0
            output_tokens = 0

            with self.client.messages.stream(
                model=self.DEEP_RESEARCH_MODEL,
                max_tokens=16384,  # Reduced for streaming stability
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": research_prompt
                    }
                ],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": max_searches
                }]
            ) as stream:
                for event in stream:
                    # Handle text events
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_delta':
                            if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                                text += event.delta.text

                # Get final message for citations and usage
                response = stream.get_final_message()

                # Extract citations from web search results
                for block in response.content:
                    if block.type == 'web_search_tool_result' and hasattr(block, 'content'):
                        for result in block.content:
                            if hasattr(result, 'url') and hasattr(result, 'title'):
                                url = result.url
                                if url not in seen_urls:
                                    seen_urls.add(url)
                                    citations.append({
                                        "url": url,
                                        "title": result.title,
                                        "snippet": getattr(result, 'snippet', '')
                                    })

                if response.usage:
                    input_tokens = response.usage.input_tokens
                    output_tokens = response.usage.output_tokens

            return ResearchResult(
                provider=self.provider_name,
                model=self.DEEP_RESEARCH_MODEL,
                mode="deep",
                text=text,
                citations=citations,
                timestamp=datetime.utcnow(),
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            )

        except Exception as e:
            return self._create_error_result(str(e), "deep")

    def _extract_response_content(self, response) -> tuple:
        """
        Extract text content and citations from Claude's response.

        Returns:
            tuple: (text, citations)
        """
        text = ""
        citations = []
        seen_urls = set()  # Deduplicate citations

        for block in response.content:
            # Extract text blocks
            if block.type == 'text' and hasattr(block, 'text'):
                text += block.text

            # Extract citations from web search results
            elif block.type == 'web_search_tool_result' and hasattr(block, 'content'):
                for result in block.content:
                    if hasattr(result, 'url') and hasattr(result, 'title'):
                        url = result.url
                        if url not in seen_urls:
                            seen_urls.add(url)
                            citations.append({
                                "url": url,
                                "title": result.title,
                                "snippet": getattr(result, 'snippet', '')
                            })

            # Also check for tool_use blocks that might contain search info
            elif block.type == 'tool_use':
                # Log search queries if needed for debugging
                pass

        return text, citations

    def multi_phase_research(self, prompt: str, company: str) -> ResearchResult:
        """
        Alternative deep research using multiple phases.

        Phase 1: Initial broad research
        Phase 2: Deep dive on key findings
        Phase 3: Verification and synthesis

        This is more expensive but can provide even more thorough results.
        """
        try:
            all_citations = []
            all_text_parts = []

            # Phase 1: Initial discovery
            phase1_prompt = f"""PHASE 1 - INITIAL DISCOVERY for {company}:

{prompt}

Focus on:
- Recent news and announcements (last 30-90 days)
- Key developments and milestones
- Official company statements

Provide a structured summary with sources. Note any areas that need deeper investigation."""

            phase1_response = self.client.messages.create(
                model=self.DEEP_RESEARCH_MODEL,
                max_tokens=16384,
                system=f"You are conducting Phase 1 of a deep research project on {company}. Focus on discovery and identification of key topics.",
                messages=[{"role": "user", "content": phase1_prompt}],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 15
                }]
            )

            phase1_text, phase1_citations = self._extract_response_content(phase1_response)
            all_text_parts.append("## Phase 1: Initial Discovery\n\n" + phase1_text)
            all_citations.extend(phase1_citations)

            # Phase 2: Verification and deep dive
            phase2_prompt = f"""PHASE 2 - VERIFICATION AND DEEP DIVE for {company}:

Based on initial findings:
{phase1_text[:3000]}  # Summary of phase 1

Now verify and expand on these findings:
1. Cross-reference key claims with additional sources
2. Search for more specific details on important topics
3. Look for contradicting information
4. Find financial data and official filings

Provide detailed, verified information with sources."""

            phase2_response = self.client.messages.create(
                model=self.DEEP_RESEARCH_MODEL,
                max_tokens=16384,
                system=f"You are conducting Phase 2 of a deep research project on {company}. Focus on verification and detailed analysis.",
                messages=[{"role": "user", "content": phase2_prompt}],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 15
                }]
            )

            phase2_text, phase2_citations = self._extract_response_content(phase2_response)
            all_text_parts.append("\n\n## Phase 2: Verification & Deep Dive\n\n" + phase2_text)
            all_citations.extend(phase2_citations)

            # Deduplicate citations
            seen_urls = set()
            unique_citations = []
            for cite in all_citations:
                if cite['url'] not in seen_urls:
                    seen_urls.add(cite['url'])
                    unique_citations.append(cite)

            return ResearchResult(
                provider=self.provider_name,
                model=self.DEEP_RESEARCH_MODEL,
                mode="deep",
                text="\n".join(all_text_parts),
                citations=unique_citations,
                timestamp=datetime.utcnow(),
                usage={
                    "input_tokens": phase1_response.usage.input_tokens + phase2_response.usage.input_tokens,
                    "output_tokens": phase1_response.usage.output_tokens + phase2_response.usage.output_tokens
                }
            )

        except Exception as e:
            return self._create_error_result(str(e), "deep")
