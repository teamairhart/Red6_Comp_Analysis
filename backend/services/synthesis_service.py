"""
Synthesis Service - Combines multiple AI model outputs into a unified report.

This service takes research outputs from multiple LLM providers and synthesizes
them into a single comprehensive report with:
- Unified narrative combining insights from all sources
- Agreement analysis (high confidence findings)
- Disagreement/conflict analysis (areas needing attention)
- Unique insights from each model
- Confidence scores based on consensus
- Model attribution throughout

(Using Gemini during development to utilize trial credits - switch back to Claude for production)
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


@dataclass
class SynthesizedInsight:
    """A synthesized insight with attribution and confidence."""
    content: str
    confidence: str  # "high", "medium", "low"
    agreeing_models: List[str]
    source_quotes: Dict[str, str]  # model -> relevant quote


@dataclass
class SynthesisReport:
    """The complete synthesized report."""
    company: str
    prompt_name: str
    executive_summary: str
    unified_analysis: str
    high_confidence_findings: List[str]  # Points where models agreed
    areas_of_disagreement: List[str]  # Points where models conflicted
    unique_insights: Dict[str, List[str]]  # model -> unique findings
    methodology_note: str
    models_used: List[str]
    generated_at: datetime
    full_markdown: str  # The complete formatted report


SYNTHESIS_PROMPT = """You are a competitive intelligence analyst tasked with synthesizing research reports from multiple AI models into a single comprehensive intelligence report.

**COMPANY BEING RESEARCHED:** {company}
**RESEARCH TOPIC:** {prompt_name}
**MODELS CONTRIBUTING:** {models}

---

## INDIVIDUAL MODEL REPORTS

{model_reports}

---

## YOUR TASK

Create a UNIFIED INTELLIGENCE REPORT that:

1. **Executive Summary** (2-3 paragraphs)
   - Synthesize the key findings across all models
   - Highlight the most important strategic insights
   - Note the overall confidence level based on model agreement

2. **High-Confidence Findings** (bullet points)
   - List findings where multiple models AGREED
   - These are your most reliable intelligence
   - For each, note which models confirmed it
   - Format: "• [Finding] (Confirmed by: Model1, Model2, Model3)"

3. **Areas of Disagreement or Uncertainty** (bullet points)
   - List points where models DISAGREED or provided conflicting information
   - Explain the different perspectives
   - These areas may need additional verification
   - Format: "• [Topic]: Model1 says X, while Model2 says Y"

4. **Unique Insights by Model** (subsections)
   - For EACH model, list 2-3 unique insights they provided that others missed
   - This captures the value of using multiple AI sources
   - Format as subsections: "### From [Model Name]" followed by bullet points

5. **Detailed Analysis** (organized sections)
   - Create a comprehensive narrative that weaves together the best information from all sources
   - Use clear section headers for different aspects (e.g., Market Position, Technology, Financials, etc.)
   - Attribute specific claims when there's uncertainty
   - Integrate tables if multiple models provided similar data

6. **Methodology Note** (1 paragraph)
   - Briefly explain this report was synthesized from {num_models} AI models
   - List the models used
   - Note the date of analysis

## IMPORTANT GUIDELINES

- DO NOT simply concatenate the reports - create a truly unified narrative
- ALWAYS attribute uncertain or conflicting information to specific models
- Use confidence indicators: [HIGH CONFIDENCE], [MEDIUM CONFIDENCE], [LOW CONFIDENCE]
- Preserve important tables and data from individual reports
- If models provide different numbers/statistics, show all with attribution
- Prioritize ACTIONABLE intelligence over generic observations
- Keep the executive summary punchy and decision-oriented

## OUTPUT FORMAT

Output the complete report in clean Markdown format. Do not include meta-commentary about the synthesis process within the report itself (save that for the Methodology Note at the end).

Begin your synthesized intelligence report now:"""


class SynthesisService:
    """
    Service for synthesizing multiple AI model outputs into unified reports.
    Uses Gemini as the synthesis model during development (to use trial credits).
    Switch back to Claude for production deployment.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        from google import genai
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"  # Fast, capable model for synthesis

    def synthesize(
        self,
        company: str,
        prompt_name: str,
        model_outputs: Dict[str, str],  # model_name -> report_content
    ) -> SynthesisReport:
        """
        Synthesize multiple model outputs into a unified report.

        Args:
            company: The company being researched
            prompt_name: The type of research/prompt used
            model_outputs: Dict mapping model names to their report content

        Returns:
            SynthesisReport with the unified analysis
        """
        if not model_outputs:
            raise ValueError("No model outputs to synthesize")

        if len(model_outputs) < 2:
            raise ValueError("Need at least 2 model outputs to synthesize")

        # Format the model reports for the prompt
        model_reports = []
        for model_name, content in model_outputs.items():
            model_reports.append(f"""
### Report from {model_name.upper()}
---
{content}
---
""")

        models_list = list(model_outputs.keys())

        # Build the synthesis prompt
        prompt = SYNTHESIS_PROMPT.format(
            company=company,
            prompt_name=prompt_name,
            models=", ".join(models_list),
            model_reports="\n\n".join(model_reports),
            num_models=len(model_outputs),
        )

        # Call Gemini to synthesize
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        synthesized_content = response.text

        # Parse out the sections (basic parsing)
        high_confidence = self._extract_section(
            synthesized_content,
            "High-Confidence Findings",
            "Areas of Disagreement"
        )

        disagreements = self._extract_section(
            synthesized_content,
            "Areas of Disagreement",
            "Unique Insights"
        )

        # Create the report
        return SynthesisReport(
            company=company,
            prompt_name=prompt_name,
            executive_summary=self._extract_section(
                synthesized_content,
                "Executive Summary",
                "High-Confidence"
            ),
            unified_analysis=synthesized_content,
            high_confidence_findings=self._parse_bullets(high_confidence),
            areas_of_disagreement=self._parse_bullets(disagreements),
            unique_insights=self._extract_unique_insights(synthesized_content, models_list),
            methodology_note=self._extract_section(
                synthesized_content,
                "Methodology",
                None
            ),
            models_used=models_list,
            generated_at=datetime.utcnow(),
            full_markdown=synthesized_content,
        )

    def _extract_section(
        self,
        content: str,
        start_marker: str,
        end_marker: Optional[str]
    ) -> str:
        """Extract a section from the synthesized content."""
        lines = content.split('\n')
        in_section = False
        section_lines = []

        for line in lines:
            if start_marker.lower() in line.lower():
                in_section = True
                continue
            if end_marker and end_marker.lower() in line.lower():
                break
            if in_section:
                section_lines.append(line)

        return '\n'.join(section_lines).strip()

    def _parse_bullets(self, section: str) -> List[str]:
        """Parse bullet points from a section."""
        bullets = []
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                bullets.append(line.lstrip('•-* ').strip())
        return bullets

    def _extract_unique_insights(
        self,
        content: str,
        models: List[str]
    ) -> Dict[str, List[str]]:
        """Extract unique insights for each model."""
        insights = {}
        for model in models:
            section = self._extract_section(
                content,
                f"From {model}",
                "From "  # Next model section or end
            )
            if not section:
                # Try alternate format
                section = self._extract_section(
                    content,
                    model.upper(),
                    None
                )
            insights[model] = self._parse_bullets(section) if section else []
        return insights


# Global instance
_synthesis_service: Optional[SynthesisService] = None


def get_synthesis_service() -> SynthesisService:
    """Get or create the global synthesis service instance."""
    global _synthesis_service
    if _synthesis_service is None:
        _synthesis_service = SynthesisService()
    return _synthesis_service
