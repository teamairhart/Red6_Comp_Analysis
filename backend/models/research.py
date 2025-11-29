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


class Citation(BaseModel):
    """A citation/source reference"""
    url: str
    title: Optional[str] = None


class ProviderResult(BaseModel):
    """Result from a single provider"""
    provider: str
    status: ResearchStatus = ResearchStatus.PENDING
    content: Optional[str] = None
    citations: list[Citation] = []
    model: Optional[str] = None
    error: Optional[str] = None


class SynthesizedReport(BaseModel):
    """A synthesized report combining multiple model outputs"""
    content: str  # The full markdown content
    models_used: list[str]  # Which models contributed
    high_confidence_findings: list[str] = []  # Points where models agreed
    areas_of_disagreement: list[str] = []  # Points where models conflicted
    unique_insights: dict[str, list[str]] = {}  # model -> unique findings
    generated_at: Optional[datetime] = None


class ResearchJob(BaseModel):
    """A research job"""
    id: str
    company: str
    prompt_id: str
    prompt_name: str
    status: ResearchStatus
    providers: list[str]
    mode: str  # "basic", "deep", or "combined"
    progress: int = 0  # 0-100 percentage
    results: list[ProviderResult] = []
    synthesized_report: Optional[SynthesizedReport] = None  # Combined report when mode=combined
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result_file: Optional[str] = None
    error: Optional[str] = None
    # Source tracking
    recommended_sources: list[str] = []  # Source IDs recommended for this research
    cited_sources: list[str] = []  # Source IDs that were actually cited in results
    # Delta analysis
    delta_report_id: Optional[str] = None  # ID of the associated delta report


class ResearchResponse(BaseModel):
    """Response when starting a research job"""
    job_id: str
    status: ResearchStatus
    message: str
