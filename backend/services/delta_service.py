"""Delta Intelligence Service - Detects what's new in research reports"""
import os
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import anthropic

from models.delta import (
    DeltaFinding,
    DeltaReport,
    DeltaSummary,
    FindingType,
    Confidence,
    Importance,
)

logger = logging.getLogger(__name__)


def get_reports_dir() -> Path:
    """Get the path to the reports directory"""
    return Path(__file__).parent.parent.parent / "reports"


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def load_historical_reports(
    company: str,
    lookback_days: int = 90,
    exclude_report_path: Optional[str] = None
) -> List[Dict]:
    """
    Load historical reports for a company within the lookback period.

    Args:
        company: Company name
        lookback_days: How many days back to look
        exclude_report_path: Path to exclude (e.g., the current report)

    Returns:
        List of report dicts with path, content, date, prompt_id, provider
    """
    reports_dir = get_reports_dir()
    company_dir = reports_dir / company

    if not company_dir.exists():
        return []

    cutoff_date = datetime.now() - timedelta(days=lookback_days)
    reports = []

    # Walk through company directory
    for item in company_dir.iterdir():
        if item.is_dir() and item.name.startswith("20"):
            # Dated subdirectory (e.g., 2025-11-28_021220)
            try:
                dir_date = datetime.strptime(item.name.split("_")[0], "%Y-%m-%d")
                if dir_date < cutoff_date:
                    continue

                for md_file in item.glob("*.md"):
                    if exclude_report_path and str(md_file) == exclude_report_path:
                        continue
                    reports.append(_parse_report_file(md_file, dir_date))
            except ValueError:
                continue
        elif item.is_file() and item.suffix == ".md":
            # Direct file in company directory
            if exclude_report_path and str(item) == exclude_report_path:
                continue
            # Use file modification time
            mod_time = datetime.fromtimestamp(item.stat().st_mtime)
            if mod_time >= cutoff_date:
                reports.append(_parse_report_file(item, mod_time))

    return [r for r in reports if r is not None]


def _parse_report_file(file_path: Path, report_date: datetime) -> Optional[Dict]:
    """Parse a report markdown file"""
    try:
        content = file_path.read_text()

        # Extract prompt and provider from filename
        # Format: prompt_name-provider.md
        filename = file_path.stem
        parts = filename.rsplit("-", 1)

        if len(parts) == 2:
            prompt_id = parts[0]
            provider = parts[1]
        else:
            prompt_id = filename
            provider = "unknown"

        return {
            "path": str(file_path),
            "content": content,
            "date": report_date,
            "prompt_id": prompt_id,
            "provider": provider,
        }
    except Exception as e:
        logger.error(f"Error parsing report {file_path}: {e}")
        return None


def get_anthropic_client() -> Optional[anthropic.Anthropic]:
    """Get Anthropic client from environment"""
    # Try loading from .env file
    env_file = get_project_root() / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == "ANTHROPIC_API_KEY":
                        os.environ["ANTHROPIC_API_KEY"] = value.strip()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-your"):
        logger.warning("Anthropic API key not configured for delta analysis")
        return None

    return anthropic.Anthropic(api_key=api_key)


DELTA_ANALYSIS_PROMPT = """You are an intelligence analyst comparing a NEW research report against HISTORICAL reports for the same company. Your task is to identify what is genuinely NEW, UPDATED, or CONTRADICTED.

## HISTORICAL CONTEXT
The following are previous reports on {company}:

{historical_context}

## NEW REPORT
{new_report}

## YOUR TASK
Analyze the NEW REPORT and identify significant findings that represent:
1. **NEW** - Information not present in any historical reports
2. **UPDATED** - Information that updates/changes something from historical reports
3. **CONTRADICTED** - Information that contradicts something stated in historical reports

For each finding, provide:
- The finding text (concise summary)
- Type: NEW, UPDATED, or CONTRADICTED
- Confidence: HIGH, MEDIUM, or LOW (how certain you are this is accurate)
- Importance: CRITICAL (immediate action needed), NOTABLE (significant), or MINOR (good to know)
- Category: Executive, Contract, Technology, Partnership, Financial, Strategy, or Other
- Previous text (for UPDATED/CONTRADICTED only - what it updates/contradicts)
- Source URL if mentioned in the report

## OUTPUT FORMAT
Return a JSON array of findings. Example:
```json
[
  {{
    "finding_text": "John Smith appointed as new CEO effective January 2025",
    "finding_type": "NEW",
    "confidence": "HIGH",
    "importance": "CRITICAL",
    "category": "Executive",
    "previous_text": null,
    "source_url": "https://example.com/article"
  }},
  {{
    "finding_text": "Contract value increased from $50M to $75M",
    "finding_type": "UPDATED",
    "confidence": "MEDIUM",
    "importance": "NOTABLE",
    "category": "Contract",
    "previous_text": "Initial contract award was $50M",
    "source_url": null
  }}
]
```

IMPORTANT:
- Only include genuinely significant findings, not minor rewording
- Be conservative - if unsure whether something is new, mark it as LOW confidence
- Focus on actionable intelligence relevant to competitive analysis
- Return ONLY the JSON array, no other text
- If there are no significant findings, return an empty array: []
"""


def run_delta_analysis(
    company: str,
    new_report_content: str,
    job_id: str,
    prompt_id: str,
    lookback_days: int = 90,
) -> Optional[DeltaReport]:
    """
    Run delta analysis comparing new research against historical reports.

    Args:
        company: Company name
        new_report_content: Content of the new research report
        job_id: ID of the research job
        prompt_id: Prompt used for the research
        lookback_days: How far back to look for comparison

    Returns:
        DeltaReport with findings, or None if analysis failed
    """
    client = get_anthropic_client()
    if not client:
        logger.error("Cannot run delta analysis - Anthropic client not available")
        return None

    # Load historical reports
    historical = load_historical_reports(company, lookback_days)

    if not historical:
        logger.info(f"No historical reports found for {company}, skipping delta analysis")
        # Return empty delta report
        return DeltaReport(
            id=str(uuid.uuid4()),
            job_id=job_id,
            company=company,
            prompt_id=prompt_id,
            findings=[],
            summary="No historical reports available for comparison.",
            compared_to_reports=[],
            created_at=datetime.utcnow(),
        )

    # Build historical context (limit to prevent token overflow)
    historical_context = _build_historical_context(historical, max_chars=50000)
    compared_report_paths = [r["path"] for r in historical[:10]]  # Track which we used

    # Build the prompt
    prompt = DELTA_ANALYSIS_PROMPT.format(
        company=company,
        historical_context=historical_context,
        new_report=new_report_content[:30000],  # Limit new report size too
    )

    try:
        logger.info(f"Running delta analysis for {company} against {len(historical)} historical reports")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = response.content[0].text

        # Parse JSON response
        findings = _parse_findings_response(response_text, job_id, company)

        # Generate summary
        summary = _generate_summary(findings)

        delta_report = DeltaReport(
            id=str(uuid.uuid4()),
            job_id=job_id,
            company=company,
            prompt_id=prompt_id,
            findings=findings,
            summary=summary,
            compared_to_reports=compared_report_paths,
            created_at=datetime.utcnow(),
        )

        logger.info(f"Delta analysis complete: {len(findings)} findings for {company}")
        return delta_report

    except Exception as e:
        logger.error(f"Delta analysis failed for {company}: {e}")
        return None


def _build_historical_context(reports: List[Dict], max_chars: int = 50000) -> str:
    """Build a condensed historical context string"""
    context_parts = []
    total_chars = 0

    # Sort by date descending (most recent first)
    reports_sorted = sorted(reports, key=lambda r: r["date"], reverse=True)

    for report in reports_sorted:
        header = f"\n### Report: {report['prompt_id']} ({report['provider']}) - {report['date'].strftime('%Y-%m-%d')}\n"
        content = report["content"]

        # Truncate individual reports if needed
        available = max_chars - total_chars - len(header)
        if available <= 0:
            break

        if len(content) > available:
            content = content[:available] + "\n[...truncated...]"

        context_parts.append(header + content)
        total_chars += len(header) + len(content)

    return "\n".join(context_parts)


def _parse_findings_response(response_text: str, job_id: str, company: str) -> List[DeltaFinding]:
    """Parse the JSON response from Claude into DeltaFinding objects"""
    findings = []

    try:
        # Try to extract JSON from response
        # Handle case where response might have markdown code blocks
        json_text = response_text.strip()
        if json_text.startswith("```"):
            # Extract from code block
            lines = json_text.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```") and not in_block:
                    in_block = True
                    continue
                elif line.startswith("```") and in_block:
                    break
                elif in_block:
                    json_lines.append(line)
            json_text = "\n".join(json_lines)

        raw_findings = json.loads(json_text)

        for raw in raw_findings:
            finding = DeltaFinding(
                id=str(uuid.uuid4()),
                report_id=job_id,
                company=company,
                finding_text=raw.get("finding_text", ""),
                finding_type=FindingType(raw.get("finding_type", "NEW")),
                confidence=Confidence(raw.get("confidence", "MEDIUM")),
                importance=Importance(raw.get("importance", "NOTABLE")),
                category=raw.get("category"),
                previous_text=raw.get("previous_text"),
                source_url=raw.get("source_url"),
                created_at=datetime.utcnow(),
            )
            findings.append(finding)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse delta findings JSON: {e}")
        logger.debug(f"Response was: {response_text[:500]}")
    except Exception as e:
        logger.error(f"Error processing delta findings: {e}")

    return findings


def _generate_summary(findings: List[DeltaFinding]) -> str:
    """Generate a text summary of the findings"""
    if not findings:
        return "No significant new findings compared to historical reports."

    critical = [f for f in findings if f.importance == Importance.CRITICAL]
    notable = [f for f in findings if f.importance == Importance.NOTABLE]

    parts = []
    parts.append(f"Found {len(findings)} delta findings.")

    if critical:
        parts.append(f" {len(critical)} CRITICAL items require attention.")
    if notable:
        parts.append(f" {len(notable)} notable updates identified.")

    # Count by type
    new_count = len([f for f in findings if f.finding_type == FindingType.NEW])
    updated_count = len([f for f in findings if f.finding_type == FindingType.UPDATED])
    contradicted_count = len([f for f in findings if f.finding_type == FindingType.CONTRADICTED])

    type_parts = []
    if new_count:
        type_parts.append(f"{new_count} new")
    if updated_count:
        type_parts.append(f"{updated_count} updated")
    if contradicted_count:
        type_parts.append(f"{contradicted_count} contradicted")

    if type_parts:
        parts.append(f" Breakdown: {', '.join(type_parts)}.")

    return "".join(parts)


def get_delta_summary(findings: List[DeltaFinding]) -> DeltaSummary:
    """Calculate summary statistics for a list of findings"""
    return DeltaSummary(
        total_findings=len(findings),
        critical_count=len([f for f in findings if f.importance == Importance.CRITICAL]),
        notable_count=len([f for f in findings if f.importance == Importance.NOTABLE]),
        minor_count=len([f for f in findings if f.importance == Importance.MINOR]),
        new_count=len([f for f in findings if f.finding_type == FindingType.NEW]),
        updated_count=len([f for f in findings if f.finding_type == FindingType.UPDATED]),
        contradicted_count=len([f for f in findings if f.finding_type == FindingType.CONTRADICTED]),
    )


# Storage for delta reports (in-memory for now, can be replaced with DB)
_delta_reports: Dict[str, DeltaReport] = {}


def save_delta_report(report: DeltaReport) -> None:
    """Save a delta report to storage"""
    _delta_reports[report.id] = report
    # Also save to file for persistence
    _save_delta_to_file(report)


def get_delta_report(report_id: str) -> Optional[DeltaReport]:
    """Get a delta report by ID"""
    return _delta_reports.get(report_id)


def get_delta_report_by_job(job_id: str) -> Optional[DeltaReport]:
    """Get a delta report by job ID"""
    for report in _delta_reports.values():
        if report.job_id == job_id:
            return report
    # Try loading from file
    return _load_delta_from_file(job_id)


def list_delta_reports(
    company: Optional[str] = None,
    limit: int = 50,
) -> List[DeltaReport]:
    """List delta reports, optionally filtered by company"""
    reports = list(_delta_reports.values())

    if company:
        reports = [r for r in reports if r.company.lower() == company.lower()]

    # Sort by created_at descending
    reports.sort(key=lambda r: r.created_at, reverse=True)

    return reports[:limit]


def get_all_findings(
    company: Optional[str] = None,
    importance: Optional[Importance] = None,
    finding_type: Optional[FindingType] = None,
    days: int = 30,
    limit: int = 100,
) -> List[DeltaFinding]:
    """Get all findings across reports with optional filters"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    all_findings = []
    for report in _delta_reports.values():
        if report.created_at < cutoff:
            continue
        if company and report.company.lower() != company.lower():
            continue

        for finding in report.findings:
            if importance and finding.importance != importance:
                continue
            if finding_type and finding.finding_type != finding_type:
                continue
            all_findings.append(finding)

    # Sort by importance (CRITICAL first) then by date
    importance_order = {Importance.CRITICAL: 0, Importance.NOTABLE: 1, Importance.MINOR: 2}
    all_findings.sort(key=lambda f: (importance_order.get(f.importance, 2), f.created_at), reverse=True)

    return all_findings[:limit]


def _save_delta_to_file(report: DeltaReport) -> None:
    """Save delta report to JSON file"""
    delta_dir = get_reports_dir() / ".delta"
    delta_dir.mkdir(exist_ok=True)

    file_path = delta_dir / f"{report.job_id}.json"

    try:
        with open(file_path, "w") as f:
            json.dump(report.model_dump(mode="json"), f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save delta report: {e}")


def _load_delta_from_file(job_id: str) -> Optional[DeltaReport]:
    """Load delta report from JSON file"""
    delta_dir = get_reports_dir() / ".delta"
    file_path = delta_dir / f"{job_id}.json"

    if not file_path.exists():
        return None

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return DeltaReport(**data)
    except Exception as e:
        logger.error(f"Failed to load delta report: {e}")
        return None


def load_all_delta_reports() -> None:
    """Load all delta reports from disk into memory"""
    delta_dir = get_reports_dir() / ".delta"
    if not delta_dir.exists():
        return

    for file_path in delta_dir.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            report = DeltaReport(**data)
            _delta_reports[report.id] = report
        except Exception as e:
            logger.error(f"Failed to load delta report {file_path}: {e}")
