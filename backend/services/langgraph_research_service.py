"""
LangGraph Deep Research Orchestration Service

Implements a multi-agent research workflow inspired by LangChain's Open Deep Research:
1. Sub-topic Decomposition: Breaks complex queries into focused sub-topics
2. Parallel Research: Runs deep research on each sub-topic using native APIs
3. Compression: Compresses each sub-topic's findings
4. Synthesis: Combines all findings into a comprehensive final report

This enhances our native deep research APIs (o3-deep-research, sonar-deep-research, etc.)
with intelligent orchestration for more thorough and structured research.
"""
import os
import asyncio
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from dataclasses import dataclass
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Import our existing research service
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.research_service import get_research_service


# State definition for the research graph
class ResearchState(TypedDict):
    """State passed through the research graph."""
    # Input
    company: str
    prompt: str
    prompt_id: str
    providers: List[str]
    mode: str

    # Decomposition output
    sub_topics: List[Dict[str, str]]  # [{topic, description, key_questions}]

    # Research output (accumulated)
    research_results: Annotated[List[Dict[str, Any]], operator.add]

    # Compression output
    compressed_findings: List[Dict[str, str]]

    # Final output
    final_report: str
    citations: List[Dict[str, str]]

    # Metadata
    status: str
    error: Optional[str]


@dataclass
class SubTopic:
    """Represents a research sub-topic."""
    topic: str
    description: str
    key_questions: List[str]


class LangGraphResearchOrchestrator:
    """
    Orchestrates deep research using LangGraph.

    Workflow:
    1. decompose_prompt → Break into sub-topics
    2. research_sub_topics → Run deep research on each (parallel)
    3. compress_findings → Compress each sub-topic's results
    4. synthesize_report → Create final comprehensive report
    """

    def __init__(self):
        self.research_service = get_research_service()

        # Initialize LLMs for orchestration tasks
        # Using GPT-4.1-mini for decomposition/compression (fast, cheap)
        # Using Claude for synthesis (best at long-form writing)
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if openai_key:
            self.decomposition_llm = ChatOpenAI(
                model="gpt-4.1-mini",
                temperature=0.3,
                api_key=openai_key
            )
            self.compression_llm = ChatOpenAI(
                model="gpt-4.1-mini",
                temperature=0.2,
                api_key=openai_key
            )
        else:
            self.decomposition_llm = None
            self.compression_llm = None

        if anthropic_key:
            self.synthesis_llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.3,
                api_key=anthropic_key
            )
        else:
            self.synthesis_llm = None

        # Build the research graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph research workflow."""
        workflow = StateGraph(ResearchState)

        # Add nodes
        workflow.add_node("decompose", self._decompose_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("compress", self._compress_node)
        workflow.add_node("synthesize", self._synthesize_node)

        # Define edges (linear flow)
        workflow.set_entry_point("decompose")
        workflow.add_edge("decompose", "research")
        workflow.add_edge("research", "compress")
        workflow.add_edge("compress", "synthesize")
        workflow.add_edge("synthesize", END)

        return workflow.compile()

    async def _decompose_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Decompose the research prompt into focused sub-topics.

        This ensures each sub-topic can be researched thoroughly without
        overwhelming a single context window.
        """
        if not self.decomposition_llm:
            # Fallback: treat entire prompt as one topic
            return {
                "sub_topics": [{
                    "topic": "Main Research",
                    "description": state["prompt"],
                    "key_questions": []
                }],
                "status": "decomposed"
            }

        system_prompt = """You are a research planning expert. Your task is to decompose a complex research request into focused sub-topics that can be researched independently.

For competitive intelligence research, good sub-topics include:
- Company overview and recent developments
- Financial performance and contracts
- Technology and product capabilities
- Strategic direction and market positioning
- Leadership and organizational structure
- Competitive landscape and differentiation

Return a JSON array of 3-5 sub-topics. Each sub-topic should have:
- topic: Short title (2-5 words)
- description: What to research for this sub-topic (1-2 sentences)
- key_questions: List of 2-3 specific questions to answer

Return ONLY valid JSON, no markdown formatting."""

        user_prompt = f"""Decompose this competitive intelligence research request about {state['company']} into focused sub-topics:

{state['prompt']}

Return a JSON array of sub-topics."""

        try:
            response = await self.decomposition_llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])

            # Parse JSON response
            import json
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            sub_topics = json.loads(content)

            return {
                "sub_topics": sub_topics,
                "status": "decomposed"
            }

        except Exception as e:
            # Fallback: use original prompt as single topic
            return {
                "sub_topics": [{
                    "topic": "Comprehensive Analysis",
                    "description": state["prompt"],
                    "key_questions": []
                }],
                "status": "decomposed",
                "error": f"Decomposition fallback: {str(e)}"
            }

    async def _research_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Run deep research on each sub-topic using our native APIs.

        Research is run in parallel across sub-topics, and for each sub-topic
        we use the specified providers with the sub-topic-specific prompt.
        """
        sub_topics = state.get("sub_topics", [])
        if not sub_topics:
            return {"research_results": [], "status": "research_failed"}

        all_results = []

        # Research each sub-topic
        for topic_info in sub_topics:
            topic = topic_info.get("topic", "Research")
            description = topic_info.get("description", "")
            key_questions = topic_info.get("key_questions", [])

            # Build focused sub-topic prompt
            sub_prompt = f"""# Research Sub-Topic: {topic}

## Company: {state['company']}

## Focus Area
{description}

## Key Questions to Answer
{chr(10).join(f'- {q}' for q in key_questions) if key_questions else '- Address the focus area thoroughly with specific, verifiable information.'}

## Research Requirements
1. Search for current information from the past 30-90 days
2. Cite specific sources with dates when available
3. Include specific numbers, dates, and financial figures
4. Note any conflicting information or uncertainty
5. Distinguish between verified facts and speculation

## Original Research Context
{state['prompt'][:2000]}"""

            try:
                # Run research using the sub-topic prompt directly
                results = await self.research_service.run_research_with_prompt_async(
                    company=state["company"],
                    prompt_content=sub_prompt,
                    mode=state["mode"],
                    providers=state["providers"]
                )

                # Store results with sub-topic context
                topic_results = {
                    "sub_topic": topic,
                    "description": description,
                    "provider_results": {}
                }

                for provider, result in results.items():
                    if not result.error:
                        topic_results["provider_results"][provider] = {
                            "text": result.text,
                            "citations": result.citations,
                            "model": result.model
                        }

                all_results.append(topic_results)

            except Exception as e:
                all_results.append({
                    "sub_topic": topic,
                    "error": str(e)
                })

        return {
            "research_results": all_results,
            "status": "researched"
        }

    async def _compress_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Compress research findings for each sub-topic.

        This reduces token count while preserving key insights, making
        the final synthesis more manageable.
        """
        if not self.compression_llm:
            # No compression, just format the findings
            compressed = []
            for result in state.get("research_results", []):
                if "error" not in result:
                    compressed.append({
                        "sub_topic": result.get("sub_topic", ""),
                        "findings": self._format_findings_simple(result)
                    })
            return {"compressed_findings": compressed, "status": "compressed"}

        compressed_findings = []

        for result in state.get("research_results", []):
            if "error" in result:
                continue

            sub_topic = result.get("sub_topic", "")
            provider_results = result.get("provider_results", {})

            if not provider_results:
                continue

            # Combine all provider results for this sub-topic
            combined_text = ""
            all_citations = []

            for provider, data in provider_results.items():
                combined_text += f"\n\n### {provider.upper()} Research:\n{data.get('text', '')[:8000]}"
                all_citations.extend(data.get("citations", []))

            # Compress the combined findings
            compress_prompt = f"""Compress the following research findings on "{sub_topic}" into a concise summary.

REQUIREMENTS:
1. Preserve all key facts, numbers, dates, and insights
2. Remove redundancy between sources
3. Note when sources agree or disagree
4. Keep critical citations
5. Target length: 1000-2000 words

RESEARCH FINDINGS:
{combined_text}

Provide a compressed summary that captures all essential information."""

            try:
                response = await self.compression_llm.ainvoke([
                    HumanMessage(content=compress_prompt)
                ])

                compressed_findings.append({
                    "sub_topic": sub_topic,
                    "findings": response.content,
                    "citations": all_citations[:20]  # Keep top citations
                })

            except Exception as e:
                # Fallback: use first provider's text truncated
                first_provider = next(iter(provider_results.values()), {})
                compressed_findings.append({
                    "sub_topic": sub_topic,
                    "findings": first_provider.get("text", "")[:3000],
                    "citations": first_provider.get("citations", [])
                })

        return {
            "compressed_findings": compressed_findings,
            "status": "compressed"
        }

    async def _synthesize_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Synthesize all compressed findings into a comprehensive final report.
        """
        compressed = state.get("compressed_findings", [])

        if not compressed:
            return {
                "final_report": "No research findings to synthesize.",
                "citations": [],
                "status": "failed"
            }

        # Gather all citations
        all_citations = []
        for finding in compressed:
            all_citations.extend(finding.get("citations", []))

        # Deduplicate citations
        seen_urls = set()
        unique_citations = []
        for cite in all_citations:
            url = cite.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_citations.append(cite)

        # Build synthesis input
        findings_text = ""
        for finding in compressed:
            findings_text += f"\n\n## {finding['sub_topic']}\n\n{finding['findings']}"

        if not self.synthesis_llm:
            # No synthesis LLM, return combined findings
            return {
                "final_report": f"# Competitive Intelligence Report: {state['company']}\n\n{findings_text}",
                "citations": unique_citations,
                "status": "completed"
            }

        synthesis_prompt = f"""You are a senior competitive intelligence analyst. Synthesize the following research findings into a comprehensive, executive-ready report on {state['company']}.

RESEARCH FINDINGS BY TOPIC:
{findings_text}

REPORT REQUIREMENTS:
1. Executive Summary (3-5 key takeaways)
2. Detailed Analysis organized by theme (not by source)
3. Competitive Implications (what this means strategically)
4. Areas of Uncertainty (where sources conflict or information is incomplete)
5. Recommendations for Further Research

QUALITY STANDARDS:
- Write for a senior executive audience
- Be specific with dates, numbers, and facts
- Distinguish between verified facts and speculation
- Note when multiple sources confirm a finding
- Highlight strategic implications

Generate a comprehensive, well-structured report."""

        try:
            response = await self.synthesis_llm.ainvoke([
                HumanMessage(content=synthesis_prompt)
            ])

            return {
                "final_report": response.content,
                "citations": unique_citations,
                "status": "completed"
            }

        except Exception as e:
            # Fallback: return combined findings
            return {
                "final_report": f"# Competitive Intelligence Report: {state['company']}\n\n{findings_text}\n\n*Note: Synthesis failed, showing raw findings.*",
                "citations": unique_citations,
                "status": "completed_with_errors",
                "error": str(e)
            }

    def _format_findings_simple(self, result: Dict) -> str:
        """Simple formatting for findings when no LLM compression available."""
        text_parts = []
        for provider, data in result.get("provider_results", {}).items():
            text_parts.append(f"### {provider}\n{data.get('text', '')[:2000]}")
        return "\n\n".join(text_parts)

    async def run_deep_research(
        self,
        company: str,
        prompt: str,
        prompt_id: str,
        providers: List[str],
        mode: str = "deep"
    ) -> Dict[str, Any]:
        """
        Run the full deep research pipeline.

        Returns:
            Dict with final_report, citations, and metadata
        """
        initial_state = ResearchState(
            company=company,
            prompt=prompt,
            prompt_id=prompt_id,
            providers=providers,
            mode=mode,
            sub_topics=[],
            research_results=[],
            compressed_findings=[],
            final_report="",
            citations=[],
            status="starting",
            error=None
        )

        try:
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)

            return {
                "final_report": final_state.get("final_report", ""),
                "citations": final_state.get("citations", []),
                "sub_topics": final_state.get("sub_topics", []),
                "status": final_state.get("status", "unknown"),
                "error": final_state.get("error")
            }

        except Exception as e:
            return {
                "final_report": "",
                "citations": [],
                "sub_topics": [],
                "status": "failed",
                "error": str(e)
            }


# Global instance
_orchestrator: Optional[LangGraphResearchOrchestrator] = None


def get_langgraph_orchestrator() -> LangGraphResearchOrchestrator:
    """Get or create the global LangGraph orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LangGraphResearchOrchestrator()
    return _orchestrator
