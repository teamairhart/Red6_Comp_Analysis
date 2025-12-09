"""Delta Intelligence Models"""
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, date
from enum import Enum


class FindingType(str, Enum):
    """Type of delta finding"""
    NEW = "NEW"  # Brand new information not in previous reports
    UPDATED = "UPDATED"  # Update to previously known information
    CONTRADICTED = "CONTRADICTED"  # Contradicts previous information


class Confidence(str, Enum):
    """Confidence level of the finding"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Importance(str, Enum):
    """Business importance of the finding"""
    CRITICAL = "CRITICAL"  # Requires immediate attention
    NOTABLE = "NOTABLE"  # Significant but not urgent
    MINOR = "MINOR"  # Good to know


class DeltaFinding(BaseModel):
    """A single delta finding - something new or changed"""
    id: str
    report_id: str
    company: str
    finding_text: str
    finding_type: FindingType
    confidence: Confidence
    importance: Importance
    category: Optional[str] = None  # e.g., "Executive", "Contract", "Technology"
    event_date: Optional[date] = None  # When the event occurred (if known)
    previous_text: Optional[str] = None  # For updates/contradictions
    source_url: Optional[str] = None  # Primary citation URL if available
    created_at: datetime

    # Enhanced context fields for better briefing utility
    importance_reasoning: Optional[str] = None  # Why is this CRITICAL/NOTABLE/MINOR?
    competitive_impact: Optional[str] = None  # How does this affect competitive dynamics?
    supporting_evidence: Optional[list[str]] = None  # Key quotes/facts backing the finding
    source_urls: Optional[list[str]] = None  # Multiple citation URLs for deeper research
    confidence_reasoning: Optional[str] = None  # Why is confidence HIGH/MEDIUM/LOW?
    action_items: Optional[list[str]] = None  # Suggested follow-up actions


class DeltaReport(BaseModel):
    """Delta analysis report for a research run"""
    id: str
    job_id: str  # Links to the ResearchJob
    company: str
    prompt_id: str
    findings: list[DeltaFinding] = []
    summary: Optional[str] = None  # AI-generated summary of key changes
    compared_to_reports: list[str] = []  # Report IDs used for comparison
    created_at: datetime


class DeltaRequest(BaseModel):
    """Request to run delta analysis"""
    job_id: str
    lookback_days: int = 90  # How far back to look for comparison


class DeltaSummary(BaseModel):
    """Summary stats for delta findings"""
    total_findings: int = 0
    critical_count: int = 0
    notable_count: int = 0
    minor_count: int = 0
    new_count: int = 0
    updated_count: int = 0
    contradicted_count: int = 0
