"""Schedule Service - Manages scheduled research jobs"""
import os
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from models.schedule import (
    ResearchSchedule,
    ScheduleConfig,
    ScheduleStatus,
    ScheduleFrequency,
    ScheduleExecution,
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
    Notification,
    DayOfWeek,
)

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[BackgroundScheduler] = None

# In-memory storage (will be replaced with DB later)
_schedules: Dict[str, ResearchSchedule] = {}
_executions: Dict[str, ScheduleExecution] = {}
_notifications: Dict[str, Notification] = {}


def get_data_dir() -> Path:
    """Get the data directory for schedule storage"""
    data_dir = Path(__file__).parent.parent.parent / "data" / "schedules"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_scheduler() -> BackgroundScheduler:
    """Get or create the global scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(
            jobstores={"default": MemoryJobStore()},
            executors={"default": {"type": "threadpool", "max_workers": 4}},
            job_defaults={"coalesce": True, "max_instances": 1},
        )
        _scheduler.start()
        logger.info("APScheduler started")
    return _scheduler


def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("APScheduler shut down")


def _build_cron_trigger(config: ScheduleConfig) -> CronTrigger:
    """Build a cron trigger from schedule config"""
    hour, minute = config.time_of_day.split(":")
    tz = pytz.timezone(config.timezone)

    if config.frequency == ScheduleFrequency.DAILY:
        return CronTrigger(hour=int(hour), minute=int(minute), timezone=tz)

    elif config.frequency == ScheduleFrequency.WEEKLY:
        # Convert day names to cron format (0=mon, 6=sun)
        day_map = {
            DayOfWeek.MONDAY: 0,
            DayOfWeek.TUESDAY: 1,
            DayOfWeek.WEDNESDAY: 2,
            DayOfWeek.THURSDAY: 3,
            DayOfWeek.FRIDAY: 4,
            DayOfWeek.SATURDAY: 5,
            DayOfWeek.SUNDAY: 6,
        }
        days = ",".join(str(day_map[d]) for d in config.days_of_week)
        return CronTrigger(
            day_of_week=days, hour=int(hour), minute=int(minute), timezone=tz
        )

    elif config.frequency == ScheduleFrequency.BIWEEKLY:
        # Run every other week on specified days
        days = ",".join(str(d.value[:3]) for d in config.days_of_week)
        return CronTrigger(
            day_of_week=days,
            hour=int(hour),
            minute=int(minute),
            week="*/2",
            timezone=tz,
        )

    elif config.frequency == ScheduleFrequency.MONTHLY:
        return CronTrigger(
            day=config.day_of_month,
            hour=int(hour),
            minute=int(minute),
            timezone=tz,
        )

    raise ValueError(f"Unknown frequency: {config.frequency}")


def _execute_scheduled_research(schedule_id: str):
    """Execute a scheduled research job"""
    from services.research_service import get_research_service
    from services.delta_service import run_delta_analysis, save_delta_report
    from models.delta import Importance

    if schedule_id not in _schedules:
        logger.error(f"Schedule {schedule_id} not found")
        return

    schedule = _schedules[schedule_id]

    if schedule.status != ScheduleStatus.ACTIVE:
        logger.info(f"Schedule {schedule_id} is not active, skipping")
        return

    execution_id = str(uuid.uuid4())
    execution = ScheduleExecution(
        id=execution_id,
        schedule_id=schedule_id,
        job_id="",  # Will be set after research starts
        started_at=datetime.utcnow(),
        status="running",
    )
    _executions[execution_id] = execution

    try:
        logger.info(f"Executing scheduled research: {schedule.name} ({schedule_id})")

        # Get the research service
        service = get_research_service()

        # Run the research
        results = service.engine.run_research(
            schedule.company,
            schedule.prompt_id,
            schedule.mode,
            schedule.providers,
        )

        # Save results
        save_info = service.save_results(
            results, schedule.company, schedule.prompt_id.replace("_", " ").title()
        )

        # Update execution
        execution.status = "completed"
        execution.completed_at = datetime.utcnow()
        execution.job_id = save_info.get("output_dir", execution_id)

        # Run delta analysis if enabled
        if schedule.run_delta_analysis:
            combined_content = []
            for provider, result in results.items():
                if result.error is None and result.text:
                    combined_content.append(f"## {provider.upper()} Results\n\n{result.text}")

            if combined_content:
                full_content = "\n\n---\n\n".join(combined_content)
                delta_report = run_delta_analysis(
                    company=schedule.company,
                    new_report_content=full_content,
                    job_id=execution_id,
                    prompt_id=schedule.prompt_id,
                    lookback_days=90,
                )
                if delta_report:
                    save_delta_report(delta_report)
                    execution.delta_report_id = delta_report.id
                    execution.critical_findings_count = len(
                        [f for f in delta_report.findings if f.importance == Importance.CRITICAL]
                    )

        # Update schedule
        schedule.last_run_at = datetime.utcnow()
        schedule.run_count += 1
        schedule.updated_at = datetime.utcnow()

        # Calculate next run
        scheduler = get_scheduler()
        job = scheduler.get_job(schedule_id)
        if job:
            schedule.next_run_at = job.next_run_time

        # Create notification
        if schedule.notify_on_complete:
            _create_notification(
                type="schedule_complete",
                title=f"Research Complete: {schedule.name}",
                message=f"Scheduled research for {schedule.company} completed successfully.",
                schedule_id=schedule_id,
                job_id=execution.job_id,
            )

        # Notify on critical findings
        if schedule.notify_on_critical and execution.critical_findings_count > 0:
            _create_notification(
                type="critical_finding",
                title=f"Critical Findings: {schedule.company}",
                message=f"Found {execution.critical_findings_count} critical findings in scheduled research.",
                schedule_id=schedule_id,
                job_id=execution.job_id,
            )

        logger.info(f"Scheduled research completed: {schedule.name}")
        _save_schedules()

    except Exception as e:
        logger.error(f"Scheduled research failed: {schedule.name} - {e}")
        execution.status = "failed"
        execution.error = str(e)
        execution.completed_at = datetime.utcnow()

        _create_notification(
            type="error",
            title=f"Research Failed: {schedule.name}",
            message=f"Scheduled research for {schedule.company} failed: {str(e)[:100]}",
            schedule_id=schedule_id,
        )


def _create_notification(
    type: str,
    title: str,
    message: str,
    schedule_id: Optional[str] = None,
    job_id: Optional[str] = None,
):
    """Create an in-app notification"""
    notification = Notification(
        id=str(uuid.uuid4()),
        type=type,
        title=title,
        message=message,
        schedule_id=schedule_id,
        job_id=job_id,
        is_read=False,
        created_at=datetime.utcnow(),
    )
    _notifications[notification.id] = notification
    return notification


def create_schedule(request: ScheduleCreateRequest) -> ResearchSchedule:
    """Create a new research schedule"""
    schedule_id = str(uuid.uuid4())
    now = datetime.utcnow()

    schedule = ResearchSchedule(
        id=schedule_id,
        name=request.name,
        description=request.description,
        status=ScheduleStatus.ACTIVE,
        company=request.company,
        prompt_id=request.prompt_id,
        providers=request.providers,
        mode=request.mode,
        config=request.config,
        created_at=now,
        updated_at=now,
        run_delta_analysis=request.run_delta_analysis,
        notify_on_complete=request.notify_on_complete,
        notify_on_critical=request.notify_on_critical,
    )

    # Add to scheduler
    scheduler = get_scheduler()
    trigger = _build_cron_trigger(request.config)
    job = scheduler.add_job(
        _execute_scheduled_research,
        trigger=trigger,
        id=schedule_id,
        args=[schedule_id],
        name=request.name,
    )
    schedule.next_run_at = job.next_run_time

    _schedules[schedule_id] = schedule
    _save_schedules()

    logger.info(f"Created schedule: {schedule.name} ({schedule_id})")
    return schedule


def update_schedule(schedule_id: str, request: ScheduleUpdateRequest) -> Optional[ResearchSchedule]:
    """Update an existing schedule"""
    if schedule_id not in _schedules:
        return None

    schedule = _schedules[schedule_id]

    # Update fields
    if request.name is not None:
        schedule.name = request.name
    if request.description is not None:
        schedule.description = request.description
    if request.company is not None:
        schedule.company = request.company
    if request.prompt_id is not None:
        schedule.prompt_id = request.prompt_id
    if request.providers is not None:
        schedule.providers = request.providers
    if request.mode is not None:
        schedule.mode = request.mode
    if request.run_delta_analysis is not None:
        schedule.run_delta_analysis = request.run_delta_analysis
    if request.notify_on_complete is not None:
        schedule.notify_on_complete = request.notify_on_complete
    if request.notify_on_critical is not None:
        schedule.notify_on_critical = request.notify_on_critical

    # Handle status change
    if request.status is not None:
        schedule.status = request.status
        scheduler = get_scheduler()
        if request.status == ScheduleStatus.ACTIVE:
            scheduler.resume_job(schedule_id)
        else:
            scheduler.pause_job(schedule_id)

    # Handle config change - need to reschedule
    if request.config is not None:
        schedule.config = request.config
        scheduler = get_scheduler()
        trigger = _build_cron_trigger(request.config)
        scheduler.reschedule_job(schedule_id, trigger=trigger)
        job = scheduler.get_job(schedule_id)
        if job:
            schedule.next_run_at = job.next_run_time

    schedule.updated_at = datetime.utcnow()
    _save_schedules()

    return schedule


def delete_schedule(schedule_id: str) -> bool:
    """Delete a schedule"""
    if schedule_id not in _schedules:
        return False

    scheduler = get_scheduler()
    try:
        scheduler.remove_job(schedule_id)
    except Exception:
        pass

    del _schedules[schedule_id]
    _save_schedules()

    logger.info(f"Deleted schedule: {schedule_id}")
    return True


def get_schedule(schedule_id: str) -> Optional[ResearchSchedule]:
    """Get a schedule by ID"""
    return _schedules.get(schedule_id)


def list_schedules(status: Optional[ScheduleStatus] = None) -> List[ResearchSchedule]:
    """List all schedules"""
    schedules = list(_schedules.values())
    if status:
        schedules = [s for s in schedules if s.status == status]
    return sorted(schedules, key=lambda s: s.created_at, reverse=True)


def get_schedule_executions(schedule_id: str, limit: int = 10) -> List[ScheduleExecution]:
    """Get execution history for a schedule"""
    executions = [e for e in _executions.values() if e.schedule_id == schedule_id]
    return sorted(executions, key=lambda e: e.started_at, reverse=True)[:limit]


def run_schedule_now(schedule_id: str) -> bool:
    """Trigger a schedule to run immediately"""
    if schedule_id not in _schedules:
        return False

    # Run in background thread
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(_execute_scheduled_research, schedule_id)

    return True


# Notification functions
def list_notifications(unread_only: bool = False, limit: int = 50) -> List[Notification]:
    """List notifications"""
    notifications = list(_notifications.values())
    if unread_only:
        notifications = [n for n in notifications if not n.is_read]
    return sorted(notifications, key=lambda n: n.created_at, reverse=True)[:limit]


def mark_notification_read(notification_id: str) -> bool:
    """Mark a notification as read"""
    if notification_id not in _notifications:
        return False
    _notifications[notification_id].is_read = True
    return True


def mark_all_notifications_read():
    """Mark all notifications as read"""
    for notification in _notifications.values():
        notification.is_read = True


def get_unread_count() -> int:
    """Get count of unread notifications"""
    return len([n for n in _notifications.values() if not n.is_read])


# Persistence
def _save_schedules():
    """Save schedules to disk"""
    data_dir = get_data_dir()
    schedules_file = data_dir / "schedules.json"

    data = {
        "schedules": [s.model_dump(mode="json") for s in _schedules.values()],
        "executions": [e.model_dump(mode="json") for e in list(_executions.values())[-100:]],  # Keep last 100
    }

    with open(schedules_file, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_schedules():
    """Load schedules from disk and register with scheduler"""
    data_dir = get_data_dir()
    schedules_file = data_dir / "schedules.json"

    if not schedules_file.exists():
        return

    try:
        with open(schedules_file, "r") as f:
            data = json.load(f)

        for s_data in data.get("schedules", []):
            schedule = ResearchSchedule(**s_data)
            _schedules[schedule.id] = schedule

            # Re-register with scheduler if active
            if schedule.status == ScheduleStatus.ACTIVE:
                scheduler = get_scheduler()
                trigger = _build_cron_trigger(schedule.config)
                job = scheduler.add_job(
                    _execute_scheduled_research,
                    trigger=trigger,
                    id=schedule.id,
                    args=[schedule.id],
                    name=schedule.name,
                    replace_existing=True,
                )
                schedule.next_run_at = job.next_run_time

        for e_data in data.get("executions", []):
            execution = ScheduleExecution(**e_data)
            _executions[execution.id] = execution

        logger.info(f"Loaded {len(_schedules)} schedules from disk")

    except Exception as e:
        logger.error(f"Failed to load schedules: {e}")
