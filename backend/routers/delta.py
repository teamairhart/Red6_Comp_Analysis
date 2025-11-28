"""Delta Intelligence API Router"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.delta import (
    DeltaReport,
    DeltaFinding,
    DeltaSummary,
    DeltaRequest,
    FindingType,
    Importance,
)
from services.delta_service import (
    run_delta_analysis,
    save_delta_report,
    get_delta_report,
    get_delta_report_by_job,
    list_delta_reports,
    get_all_findings,
    get_delta_summary,
    load_all_delta_reports,
)
from routers.research import jobs
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/delta", tags=["delta"])

# Load existing delta reports on startup
load_all_delta_reports()


@router.post("/analyze", response_model=DeltaReport)
async def analyze_delta(request: DeltaRequest):
    """
    Run delta analysis on a completed research job.
    Compares the job's results against historical reports.
    """
    job_id = request.job_id

    # Check if job exists and is completed
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    if job.status.value != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before delta analysis")

    # Get the combined content from all successful providers
    combined_content = []
    for result in job.results:
        if result.content:
            combined_content.append(f"## {result.provider.upper()} Results\n\n{result.content}")

    if not combined_content:
        raise HTTPException(status_code=400, detail="No content available for delta analysis")

    full_content = "\n\n---\n\n".join(combined_content)

    # Run delta analysis
    delta_report = run_delta_analysis(
        company=job.company,
        new_report_content=full_content,
        job_id=job_id,
        prompt_id=job.prompt_id,
        lookback_days=request.lookback_days,
    )

    if not delta_report:
        raise HTTPException(status_code=500, detail="Delta analysis failed")

    # Save the report
    save_delta_report(delta_report)

    return delta_report


@router.get("/report/{report_id}", response_model=DeltaReport)
async def get_report(report_id: str):
    """Get a specific delta report by ID"""
    report = get_delta_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Delta report not found: {report_id}")
    return report


@router.get("/job/{job_id}", response_model=DeltaReport)
async def get_report_by_job(job_id: str):
    """Get the delta report for a specific research job"""
    report = get_delta_report_by_job(job_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"No delta report found for job: {job_id}")
    return report


@router.get("/reports", response_model=List[DeltaReport])
async def list_reports(
    company: Optional[str] = Query(None, description="Filter by company name"),
    limit: int = Query(50, ge=1, le=100, description="Maximum reports to return"),
):
    """List all delta reports, optionally filtered by company"""
    return list_delta_reports(company=company, limit=limit)


@router.get("/findings", response_model=List[DeltaFinding])
async def get_findings(
    company: Optional[str] = Query(None, description="Filter by company"),
    importance: Optional[str] = Query(None, description="Filter by importance: CRITICAL, NOTABLE, MINOR"),
    finding_type: Optional[str] = Query(None, description="Filter by type: NEW, UPDATED, CONTRADICTED"),
    days: int = Query(30, ge=1, le=365, description="Look back N days"),
    limit: int = Query(100, ge=1, le=500, description="Maximum findings to return"),
):
    """
    Get all findings across reports with optional filters.
    Useful for building the Intelligence Briefing view.
    """
    # Convert string params to enums
    imp = Importance(importance) if importance else None
    ft = FindingType(finding_type) if finding_type else None

    findings = get_all_findings(
        company=company,
        importance=imp,
        finding_type=ft,
        days=days,
        limit=limit,
    )

    return findings


@router.get("/briefing", response_model=dict)
async def get_briefing(
    days: int = Query(7, ge=1, le=90, description="Look back N days"),
):
    """
    Get an intelligence briefing with summary stats and critical findings.
    Returns a structured view for the briefing page.
    """
    # Get all findings for the period
    all_findings = get_all_findings(days=days, limit=500)

    # Calculate summary
    summary = get_delta_summary(all_findings)

    # Get critical findings
    critical = [f for f in all_findings if f.importance == Importance.CRITICAL]

    # Group by company
    by_company = {}
    for finding in all_findings:
        if finding.company not in by_company:
            by_company[finding.company] = []
        by_company[finding.company].append(finding.model_dump(mode="json"))

    # Get recent reports
    reports = list_delta_reports(limit=10)

    return {
        "period_days": days,
        "summary": summary.model_dump(),
        "critical_findings": [f.model_dump(mode="json") for f in critical[:10]],
        "findings_by_company": by_company,
        "recent_reports": [r.model_dump(mode="json") for r in reports],
    }


@router.get("/company/{company}/timeline", response_model=List[DeltaFinding])
async def get_company_timeline(
    company: str,
    days: int = Query(90, ge=1, le=365, description="Look back N days"),
    limit: int = Query(100, ge=1, le=500, description="Maximum findings"),
):
    """
    Get chronological timeline of findings for a specific company.
    Ordered by date with most recent first.
    """
    findings = get_all_findings(company=company, days=days, limit=limit)

    # Sort by created_at descending
    findings.sort(key=lambda f: f.created_at, reverse=True)

    return findings
