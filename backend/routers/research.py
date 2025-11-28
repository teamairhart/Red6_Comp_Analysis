"""Research API Router"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from models.research import (
    ResearchRequest,
    ResearchResponse,
    ResearchJob,
    ResearchStatus,
    ResearchProgress,
)
from datetime import datetime
import uuid
import asyncio
from typing import Dict

router = APIRouter(prefix="/api/research", tags=["research"])

# In-memory job storage (will be replaced with database later)
jobs: Dict[str, ResearchJob] = {}

# WebSocket connections for progress updates
active_connections: Dict[str, WebSocket] = {}


@router.post("", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
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

    # TODO: Actually start the research job in background
    # For now, just return the job ID

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
