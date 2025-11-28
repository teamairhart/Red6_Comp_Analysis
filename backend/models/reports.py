"""Report models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Report(BaseModel):
    """A generated research report"""
    id: str
    filename: str
    company: str
    prompt_id: str
    prompt_name: str
    created_at: datetime
    file_size: int
    content: Optional[str] = None  # Only included when fetching single report


class ReportListResponse(BaseModel):
    """Response containing list of reports"""
    reports: list[Report]
    total: int
