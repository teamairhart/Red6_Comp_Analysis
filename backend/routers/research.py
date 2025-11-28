"""Research API Router"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import Response
from models.research import (
    ResearchRequest,
    ResearchResponse,
    ResearchJob,
    ResearchStatus,
    ResearchProgress,
    ProviderResult,
)
from services.research_service import get_research_service
from services.source_service import (
    get_prompt_keywords,
    find_relevant_sources,
    format_sources_for_prompt,
    match_citations_to_sources,
    update_source_hit_counts,
)
from services.delta_service import run_delta_analysis, save_delta_report
from datetime import datetime
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Literal
import logging
import traceback
import threading
import markdown

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])

# In-memory job storage (will be replaced with database later)
jobs: Dict[str, ResearchJob] = {}

# WebSocket connections for progress updates
active_connections: Dict[str, WebSocket] = {}

# Thread pool for running research tasks
_executor = ThreadPoolExecutor(max_workers=4)


def _run_research_sync(job_id: str):
    """Synchronous function to run research in a background thread."""
    if job_id not in jobs:
        logger.error(f"Job {job_id} not found in jobs dict")
        return

    job = jobs[job_id]
    service = get_research_service()

    try:
        # Update status to running
        job.status = ResearchStatus.RUNNING
        job.updated_at = datetime.utcnow()

        # Initialize provider results as pending
        job.results = [
            ProviderResult(provider=p, status=ResearchStatus.PENDING)
            for p in job.providers
        ]
        job.progress = 10

        # Find relevant sources for this prompt
        prompt_keywords = get_prompt_keywords(job.prompt_id)
        relevant_sources = find_relevant_sources(prompt_keywords, limit=5)
        source_hints = format_sources_for_prompt(relevant_sources)

        # Store recommended source IDs on job for later reference
        job.recommended_sources = [s["id"] for s in relevant_sources]

        logger.info(f"Starting research for job {job_id}: {job.company} - {job.prompt_id}")
        logger.info(f"Found {len(relevant_sources)} relevant sources for prompt keywords: {prompt_keywords}")

        # Run the research synchronously
        # Note: source_hints can be appended to the prompt if the engine supports it
        results = service.engine.run_research(
            job.company,
            job.prompt_id,
            job.mode,
            job.providers
        )

        logger.info(f"Research completed for job {job_id}, processing results...")

        # Collect all citations for source matching
        all_citations = []

        # Update job with results
        job.results = []
        for provider, result in results.items():
            if result.error is None:
                # Convert citations to the expected format
                citations = [
                    {"url": c.get("url", ""), "title": c.get("title", "")}
                    for c in (result.citations or [])
                ]
                all_citations.extend(citations)

                job.results.append(ProviderResult(
                    provider=provider,
                    status=ResearchStatus.COMPLETED,
                    content=result.text,
                    citations=citations,
                    model=result.model,
                ))
            else:
                job.results.append(ProviderResult(
                    provider=provider,
                    status=ResearchStatus.FAILED,
                    error=result.error,
                ))

        # Match citations to curated sources and update hit counts
        if all_citations:
            matched_source_ids = match_citations_to_sources(all_citations)
            if matched_source_ids:
                job.cited_sources = matched_source_ids
                update_source_hit_counts(matched_source_ids)
                logger.info(f"Matched {len(matched_source_ids)} curated sources: {matched_source_ids}")

        # Save results to disk
        save_info = service.save_results(results, job.company, job.prompt_name)
        job.result_file = save_info.get("output_dir")

        # Mark job as complete
        job.status = ResearchStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

        logger.info(f"Research job {job_id} completed successfully")

        # Run delta analysis in background (non-blocking)
        try:
            # Combine all successful results for delta analysis
            combined_content = []
            for pr in job.results:
                if pr.content:
                    combined_content.append(f"## {pr.provider.upper()} Results\n\n{pr.content}")

            if combined_content:
                full_content = "\n\n---\n\n".join(combined_content)
                delta_report = run_delta_analysis(
                    company=job.company,
                    new_report_content=full_content,
                    job_id=job_id,
                    prompt_id=job.prompt_id,
                    lookback_days=90,
                )
                if delta_report:
                    save_delta_report(delta_report)
                    job.delta_report_id = delta_report.id
                    logger.info(f"Delta analysis complete for job {job_id}: {len(delta_report.findings)} findings")
        except Exception as delta_err:
            logger.warning(f"Delta analysis failed for job {job_id}: {delta_err}")

    except Exception as e:
        logger.error(f"Research job {job_id} failed: {e}\n{traceback.format_exc()}")
        job.status = ResearchStatus.FAILED
        job.error = str(e)
        job.updated_at = datetime.utcnow()


@router.post("", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research job"""
    job_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Create job record
    job = ResearchJob(
        id=job_id,
        company=request.company,
        prompt_id=request.prompt_id,
        prompt_name=request.prompt_id.replace("_", " ").title(),  # Simple name for now
        status=ResearchStatus.PENDING,
        providers=request.providers,
        mode=request.mode,
        created_at=now,
        updated_at=now,
    )

    jobs[job_id] = job

    # Start the research job in background thread
    _executor.submit(_run_research_sync, job_id)

    return ResearchResponse(
        job_id=job_id,
        status=ResearchStatus.PENDING,
        message=f"Research job created for {request.company}"
    )


@router.get("/{job_id}", response_model=ResearchJob)
async def get_job(job_id: str):
    """Get the status of a research job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    return jobs[job_id]


@router.get("", response_model=list[ResearchJob])
async def list_jobs(limit: int = 10):
    """List recent research jobs"""
    sorted_jobs = sorted(jobs.values(), key=lambda j: j.created_at, reverse=True)
    return sorted_jobs[:limit]


@router.websocket("/ws/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job progress updates"""
    await websocket.accept()
    active_connections[job_id] = websocket

    try:
        while True:
            # Keep connection alive and send progress updates
            if job_id in jobs:
                job = jobs[job_id]
                progress = ResearchProgress(
                    job_id=job_id,
                    status=job.status,
                    current_step="Processing...",
                    progress_percent=50,  # Placeholder
                    timestamp=datetime.utcnow(),
                )
                await websocket.send_json(progress.model_dump(mode="json"))

                if job.status in [ResearchStatus.COMPLETED, ResearchStatus.FAILED]:
                    break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    finally:
        if job_id in active_connections:
            del active_connections[job_id]


@router.get("/{job_id}/export/{provider}")
async def export_result(
    job_id: str,
    provider: str,
    format: Literal["md", "html", "txt"] = "md"
):
    """Export a specific provider's result in various formats"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]

    if job.status != ResearchStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed yet")

    # Find the provider result
    result = next((r for r in job.results if r.provider == provider), None)
    if not result:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found in results")

    if not result.content:
        raise HTTPException(status_code=400, detail="No content available for export")

    content = result.content
    filename = f"{job.company}_{job.prompt_id}_{provider}"

    if format == "md":
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename}.md"'}
        )
    elif format == "html":
        # Convert markdown to HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{job.company} - {job.prompt_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #eee; padding-bottom: 0.5rem; }}
        h2 {{ color: #333; margin-top: 2rem; }}
        h3 {{ color: #555; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        code {{ background-color: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 1rem; overflow-x: auto; border-radius: 5px; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 1rem 0; padding-left: 1rem; color: #666; }}
    </style>
</head>
<body>
{markdown.markdown(content, extensions=['tables', 'fenced_code'])}
</body>
</html>"""
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{filename}.html"'}
        )
    else:  # txt
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{filename}.txt"'}
        )
