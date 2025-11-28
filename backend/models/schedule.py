"""Schedule Models for automated research"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time
from enum import Enum


class ScheduleFrequency(str, Enum):
    """How often to run the scheduled research"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class DayOfWeek(str, Enum):
    """Days of the week for weekly schedules"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class ScheduleStatus(str, Enum):
    """Status of a schedule"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class ScheduleConfig(BaseModel):
    """Configuration for a research schedule"""
    frequency: ScheduleFrequency
    time_of_day: str = "09:00"  # HH:MM format
    days_of_week: List[DayOfWeek] = [DayOfWeek.MONDAY]  # For weekly schedules
    day_of_month: int = 1  # For monthly schedules (1-28)
    timezone: str = "America/New_York"


class ResearchSchedule(BaseModel):
    """A scheduled research job"""
    id: str
    name: str
    description: Optional[str] = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE

    # What to research
    company: str
    prompt_id: str
    providers: List[str] = ["xai", "google"]
    mode: str = "basic"

    # When to run
    config: ScheduleConfig

    # Tracking
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    run_count: int = 0

    # Options
    run_delta_analysis: bool = True
    notify_on_complete: bool = True
    notify_on_critical: bool = True  # Notify if critical findings


class ScheduleCreateRequest(BaseModel):
    """Request to create a new schedule"""
    name: str
    description: Optional[str] = None
    company: str
    prompt_id: str
    providers: List[str] = ["xai", "google"]
    mode: str = "basic"
    config: ScheduleConfig
    run_delta_analysis: bool = True
    notify_on_complete: bool = True
    notify_on_critical: bool = True


class ScheduleUpdateRequest(BaseModel):
    """Request to update a schedule"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ScheduleStatus] = None
    company: Optional[str] = None
    prompt_id: Optional[str] = None
    providers: Optional[List[str]] = None
    mode: Optional[str] = None
    config: Optional[ScheduleConfig] = None
    run_delta_analysis: Optional[bool] = None
    notify_on_complete: Optional[bool] = None
    notify_on_critical: Optional[bool] = None


class ScheduleExecution(BaseModel):
    """Record of a schedule execution"""
    id: str
    schedule_id: str
    job_id: str  # Links to ResearchJob
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # pending, running, completed, failed
    error: Optional[str] = None
    delta_report_id: Optional[str] = None
    critical_findings_count: int = 0


class Notification(BaseModel):
    """In-app notification"""
    id: str
    type: str  # schedule_complete, critical_finding, error
    title: str
    message: str
    schedule_id: Optional[str] = None
    job_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime
