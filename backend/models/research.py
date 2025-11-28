"""Research models"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class ResearchStatus(str, Enum):
    """Status of a research job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    """Request to start a research job"""
    company: str
    prompt_id: str
    providers: list[str] = ["xai", "google"]
    mode: str = "basic"  # basic or deep


class ResearchProgress(BaseModel):
    """Progress update for a research job"""
    job_id: str
    status: ResearchStatus
    current_step: str
    progress_percent: int
    message: Optional[str] = None
    timestamp: datetime


class ResearchJob(BaseModel):
    """A research job"""
    id: str
    company: str
    prompt_id: str
    prompt_name: str
    status: ResearchStatus
    providers: list[str]
    mode: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result_file: Optional[str] = None
    error: Optional[str] = None


class ResearchResponse(BaseModel):
    """Response when starting a research job"""
    job_id: str
    status: ResearchStatus
    message: str
