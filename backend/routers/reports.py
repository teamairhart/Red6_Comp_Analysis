"""Reports API Router"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from models.reports import Report, ReportListResponse
from datetime import datetime
import os
import re

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_reports_dir() -> Path:
    """Get the reports directory path"""
    return Path(__file__).parent.parent.parent / "reports"


def parse_report_filename(filename: str) -> dict:
    """Parse a report filename to extract metadata"""
    # Expected format: Company_Name_prompt_id_YYYYMMDD_HHMMSS.md
    # Example: BAE_Systems_org_structure_and_hiring_20251127_143022.md

    base = filename.replace(".md", "")
    parts = base.split("_")

    # Try to extract date from the end
    date_str = None
    time_str = None

    if len(parts) >= 2:
        # Check if last two parts are date/time
        if parts[-1].isdigit() and len(parts[-1]) == 6:
            time_str = parts[-1]
            if parts[-2].isdigit() and len(parts[-2]) == 8:
                date_str = parts[-2]
                parts = parts[:-2]

    # Now try to identify company vs prompt
    # This is a heuristic - company names are typically at the start
    company_parts = []
    prompt_parts = []

    # Known prompt prefixes
    known_prompts = [
        "org_structure", "executive_movements", "strategic_direction",
        "products_and_pipeline", "technology_roadmap", "teaming_relationships",
        "ma_activity", "rnd_investments", "program_execution", "patents_and_ip",
        "contract_awards", "procurement_opportunities", "multi_primary",
        "multi_cross"
    ]

    found_prompt = False
    for i, part in enumerate(parts):
        if not found_prompt:
            # Check if this starts a known prompt
            remaining = "_".join(parts[i:])
            for prompt in known_prompts:
                if remaining.startswith(prompt):
                    prompt_parts = parts[i:]
                    found_prompt = True
                    break
            if not found_prompt:
                company_parts.append(part)
        else:
            break

    company = " ".join(company_parts) if company_parts else "Unknown"
    prompt_id = "_".join(prompt_parts) if prompt_parts else "unknown"

    created_at = datetime.now()
    if date_str and time_str:
        try:
            created_at = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
        except ValueError:
            pass

    return {
        "company": company,
        "prompt_id": prompt_id,
        "created_at": created_at,
    }


@router.get("", response_model=ReportListResponse)
async def list_reports(company: str = None, prompt_id: str = None, limit: int = 50):
    """List available reports with optional filtering"""
    reports_dir = get_reports_dir()
    reports = []

    if not reports_dir.exists():
        return ReportListResponse(reports=[], total=0)

    for filepath in reports_dir.glob("*.md"):
        metadata = parse_report_filename(filepath.name)

        # Apply filters
        if company and company.lower() not in metadata["company"].lower():
            continue
        if prompt_id and prompt_id not in metadata["prompt_id"]:
            continue

        reports.append(Report(
            id=filepath.stem,
            filename=filepath.name,
            company=metadata["company"],
            prompt_id=metadata["prompt_id"],
            prompt_name=metadata["prompt_id"].replace("_", " ").title(),
            created_at=metadata["created_at"],
            file_size=filepath.stat().st_size,
        ))

    # Sort by date, newest first
    reports.sort(key=lambda r: r.created_at, reverse=True)

    return ReportListResponse(
        reports=reports[:limit],
        total=len(reports)
    )


@router.get("/{report_id}", response_model=Report)
async def get_report(report_id: str):
    """Get a specific report with its content"""
    reports_dir = get_reports_dir()
    filepath = reports_dir / f"{report_id}.md"

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

    metadata = parse_report_filename(filepath.name)
    content = filepath.read_text()

    return Report(
        id=report_id,
        filename=filepath.name,
        company=metadata["company"],
        prompt_id=metadata["prompt_id"],
        prompt_name=metadata["prompt_id"].replace("_", " ").title(),
        created_at=metadata["created_at"],
        file_size=filepath.stat().st_size,
        content=content,
    )


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """Download a report as a file"""
    reports_dir = get_reports_dir()
    filepath = reports_dir / f"{report_id}.md"

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

    return FileResponse(
        path=filepath,
        filename=filepath.name,
        media_type="text/markdown"
    )
