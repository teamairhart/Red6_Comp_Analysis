"""
Synthesis Agent - Cross-validates and consolidates research from multiple LLM providers.

This agent takes research results from OpenAI, Anthropic, Google, and xAI,
identifies agreements/discrepancies, and generates a unified report.
"""
import anthropic
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from .base_researcher import ResearchResult


@dataclass
class SynthesisResult:
    """Result from the synthesis agent."""
    synthesized_report: str
    provider_agreement_score: float  # 0-1 score of how much providers agreed
    key_findings: List[str]
    discrepancies: List[Dict]
    source_summary: Dict[str, int]  # provider -> citation count
    timestamp: datetime
    model_used: str


class SynthesisAgent:
    """
    Agent that cross-validates and synthesizes research from multiple providers.
    Uses Claude as the synthesis engine for its strong reasoning capabilities.
    """

    # Use Claude for synthesis - strong at reasoning and comparison
    SYNTHESIS_MODEL = "claude-opus-4-5-20251101"

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def synthesize(
        self,
        results: List[ResearchResult],
        company: str,
        prompt_name: str
    ) -> SynthesisResult:
        """
        Synthesize multiple research results into a consolidated report.

        Args:
            results: List of ResearchResult from different providers
            company: The company being researched
            prompt_name: The research prompt used

        Returns:
            SynthesisResult with consolidated findings
        """
        # Filter out failed results
        valid_results = [r for r in results if not r.text.startswith("ERROR")]

        if not valid_results:
            return SynthesisResult(
                synthesized_report="ERROR: No valid research results to synthesize.",
                provider_agreement_score=0.0,
                key_findings=[],
                discrepancies=[],
                source_summary={},
                timestamp=datetime.utcnow(),
                model_used=self.SYNTHESIS_MODEL
            )

        if len(valid_results) == 1:
            # Only one result - return it with a note
            return SynthesisResult(
                synthesized_report=f"[Single Source Report - No Cross-Validation]\n\nSource: {valid_results[0].provider}\n\n{valid_results[0].text}",
                provider_agreement_score=1.0,
                key_findings=["Single source - no cross-validation possible"],
                discrepancies=[],
                source_summary={valid_results[0].provider: len(valid_results[0].citations)},
                timestamp=datetime.utcnow(),
                model_used=self.SYNTHESIS_MODEL
            )

        # Build the synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(valid_results, company, prompt_name)

        try:
            response = self.client.messages.create(
                model=self.SYNTHESIS_MODEL,
                max_tokens=16384,
                messages=[
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ],
                system=self._get_system_prompt()
            )

            # Extract the synthesized report
            synthesized_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    synthesized_text += block.text

            # Parse the response to extract structured data
            key_findings, discrepancies, agreement_score = self._parse_synthesis_response(synthesized_text)

            # Build source summary
            source_summary = {r.provider: len(r.citations) for r in valid_results}

            return SynthesisResult(
                synthesized_report=synthesized_text,
                provider_agreement_score=agreement_score,
                key_findings=key_findings,
                discrepancies=discrepancies,
                source_summary=source_summary,
                timestamp=datetime.utcnow(),
                model_used=self.SYNTHESIS_MODEL
            )

        except Exception as e:
            return SynthesisResult(
                synthesized_report=f"ERROR: Synthesis failed - {str(e)}",
                provider_agreement_score=0.0,
                key_findings=[],
                discrepancies=[],
                source_summary={},
                timestamp=datetime.utcnow(),
                model_used=self.SYNTHESIS_MODEL
            )

    def _get_system_prompt(self) -> str:
        """System prompt for the synthesis agent."""
        return """You are a Competitive Intelligence Synthesis Agent for Red 6, a defense technology company.

Your role is to cross-validate and synthesize research reports from multiple AI providers (OpenAI, Anthropic, Google, xAI) into a single, authoritative intelligence report.

CRITICAL GUIDELINES:

1. CROSS-VALIDATION
   - Compare facts across all provider reports
   - Identify where providers AGREE (high confidence)
   - Identify where providers DISAGREE (flag for review)
   - Note information that only ONE provider found (medium confidence)

2. SOURCE ATTRIBUTION
   - Cite which providers support each claim
   - Use format: [OpenAI, Anthropic] or [Google only]
   - Prioritize claims with multiple provider agreement

3. DISCREPANCY HANDLING
   - When providers contradict, present BOTH versions
   - Assess which is more likely correct based on source quality
   - Flag unresolved conflicts clearly

4. CONFIDENCE LEVELS
   - [HIGH]: 3+ providers agree with citations
   - [MEDIUM]: 2 providers agree OR 1 provider with strong citations
   - [LOW]: Single provider, no citations
   - [CONFLICT]: Providers disagree

5. OUTPUT FORMAT
   Your report MUST include these sections:

   ## Executive Summary
   (Key findings with confidence levels)

   ## Cross-Validated Findings
   (Facts confirmed by multiple providers)

   ## Single-Source Findings
   (Information from only one provider - note which one)

   ## Discrepancies & Conflicts
   (Where providers disagreed - present both sides)

   ## Provider Agreement Score
   (Estimate 0-100% how much providers agreed)

   ## Consolidated Intelligence Report
   (The final synthesized report for Red 6)

Be rigorous, objective, and always prioritize accuracy over completeness."""

    def _build_synthesis_prompt(
        self,
        results: List[ResearchResult],
        company: str,
        prompt_name: str
    ) -> str:
        """Build the prompt for synthesis."""

        prompt = f"""# SYNTHESIS REQUEST

**Company:** {company}
**Research Topic:** {prompt_name}
**Number of Provider Reports:** {len(results)}
**Providers:** {', '.join([r.provider.upper() for r in results])}

---

# PROVIDER REPORTS

Please cross-validate and synthesize the following research reports:

"""

        for i, result in enumerate(results, 1):
            prompt += f"""
---
## REPORT {i}: {result.provider.upper()}
**Model:** {result.model}
**Mode:** {result.mode}
**Citations:** {len(result.citations)}
**Generated:** {result.timestamp}

### Content:
{result.text}

### Sources Cited:
"""
            if result.citations:
                for j, citation in enumerate(result.citations[:20], 1):  # Limit to 20 citations
                    title = citation.get('title', 'No title')
                    url = citation.get('url', 'No URL')
                    prompt += f"{j}. {title} - {url}\n"
            else:
                prompt += "(No structured citations provided)\n"

        prompt += """
---

# YOUR TASK

1. Carefully read ALL provider reports above
2. Cross-validate the facts - what do providers agree/disagree on?
3. Generate a synthesized report following the format in your instructions
4. Be explicit about confidence levels and source attribution
5. Flag any contradictions or discrepancies

Generate the synthesis report now:
"""

        return prompt

    def _parse_synthesis_response(self, response_text: str) -> tuple:
        """
        Parse the synthesis response to extract structured data.
        Returns (key_findings, discrepancies, agreement_score)
        """
        key_findings = []
        discrepancies = []
        agreement_score = 0.75  # Default

        # Try to extract agreement score
        import re
        score_match = re.search(r'Agreement Score[:\s]*(\d+)%', response_text, re.IGNORECASE)
        if score_match:
            agreement_score = int(score_match.group(1)) / 100.0

        # Extract findings marked with [HIGH] or confirmed
        high_conf_matches = re.findall(r'\[HIGH\][:\s]*(.+?)(?=\n|$)', response_text)
        key_findings.extend(high_conf_matches[:10])  # Limit to 10

        # Extract discrepancies/conflicts
        conflict_matches = re.findall(r'\[CONFLICT\][:\s]*(.+?)(?=\n|$)', response_text)
        for conflict in conflict_matches[:5]:  # Limit to 5
            discrepancies.append({
                "description": conflict,
                "severity": "medium"
            })

        return key_findings, discrepancies, agreement_score


def format_synthesis_report(result: SynthesisResult, company: str, prompt_name: str) -> str:
    """Format a SynthesisResult as a markdown report."""

    timestamp_display = result.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

    report = f"""# Synthesized Intelligence Report

**Company:** {company}
**Research Topic:** {prompt_name}
**Synthesis Model:** {result.model_used}
**Generated:** {timestamp_display}

---

## Provider Summary

| Provider | Citations |
|----------|-----------|
"""

    for provider, count in result.source_summary.items():
        report += f"| {provider.upper()} | {count} |\n"

    report += f"""
**Provider Agreement Score:** {result.provider_agreement_score:.0%}

---

{result.synthesized_report}
"""

    if result.discrepancies:
        report += "\n---\n\n## Flagged Discrepancies\n\n"
        for i, disc in enumerate(result.discrepancies, 1):
            report += f"{i}. {disc['description']} (Severity: {disc['severity']})\n"

    return report


def save_synthesis_report(
    result: SynthesisResult,
    company: str,
    prompt_name: str,
    output_dir: str
) -> str:
    """
    Save synthesis report to the specified output directory.

    Args:
        result: SynthesisResult from synthesis agent
        company: Company name
        prompt_name: Research prompt name
        output_dir: Directory to save to (should be timestamped folder)

    Returns:
        Path to saved file
    """
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Format the report
    formatted_report = format_synthesis_report(result, company, prompt_name)

    # Save with SYNTHESIZED suffix
    filename = f"{prompt_name}-SYNTHESIZED.md"
    filepath = output_path / filename
    filepath.write_text(formatted_report)

    return str(filepath)
