"""Schedule API Router"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.schedule import (
    ResearchSchedule,
    ScheduleStatus,
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
    ScheduleExecution,
    Notification,
)
from services.schedule_service import (
    create_schedule,
    update_schedule,
    delete_schedule,
    get_schedule,
    list_schedules,
    get_schedule_executions,
    run_schedule_now,
    list_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    get_unread_count,
    load_schedules,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/schedules", tags=["schedules"])

# Load existing schedules on startup
load_schedules()


@router.post("", response_model=ResearchSchedule)
async def create_new_schedule(request: ScheduleCreateRequest):
    """Create a new research schedule"""
    try:
        schedule = create_schedule(request)
        return schedule
    except Exception as e:
        logger.error(f"Failed to create schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[ResearchSchedule])
async def get_all_schedules(
    status: Optional[str] = Query(None, description="Filter by status: active, paused, disabled"),
):
    """List all schedules"""
    status_enum = ScheduleStatus(status) if status else None
    return list_schedules(status=status_enum)


@router.get("/{schedule_id}", response_model=ResearchSchedule)
async def get_schedule_by_id(schedule_id: str):
    """Get a specific schedule"""
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return schedule


@router.put("/{schedule_id}", response_model=ResearchSchedule)
async def update_existing_schedule(schedule_id: str, request: ScheduleUpdateRequest):
    """Update a schedule"""
    schedule = update_schedule(schedule_id, request)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return schedule


@router.delete("/{schedule_id}")
async def delete_existing_schedule(schedule_id: str):
    """Delete a schedule"""
    if not delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return {"message": "Schedule deleted"}


@router.post("/{schedule_id}/run")
async def trigger_schedule_run(schedule_id: str):
    """Trigger a schedule to run immediately"""
    if not run_schedule_now(schedule_id):
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return {"message": "Schedule triggered"}


@router.post("/{schedule_id}/pause")
async def pause_schedule(schedule_id: str):
    """Pause a schedule"""
    request = ScheduleUpdateRequest(status=ScheduleStatus.PAUSED)
    schedule = update_schedule(schedule_id, request)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return schedule


@router.post("/{schedule_id}/resume")
async def resume_schedule(schedule_id: str):
    """Resume a paused schedule"""
    request = ScheduleUpdateRequest(status=ScheduleStatus.ACTIVE)
    schedule = update_schedule(schedule_id, request)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return schedule


@router.get("/{schedule_id}/executions", response_model=List[ScheduleExecution])
async def get_executions(
    schedule_id: str,
    limit: int = Query(10, ge=1, le=100),
):
    """Get execution history for a schedule"""
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Schedule not found: {schedule_id}")
    return get_schedule_executions(schedule_id, limit=limit)


# Notification endpoints
@router.get("/notifications/all", response_model=List[Notification])
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
):
    """Get notifications"""
    return list_notifications(unread_only=unread_only, limit=limit)


@router.get("/notifications/count")
async def get_notification_count():
    """Get unread notification count"""
    return {"unread_count": get_unread_count()}


@router.post("/notifications/{notification_id}/read")
async def mark_read(notification_id: str):
    """Mark a notification as read"""
    if not mark_notification_read(notification_id):
        raise HTTPException(status_code=404, detail=f"Notification not found: {notification_id}")
    return {"message": "Notification marked as read"}


@router.post("/notifications/read-all")
async def mark_all_read():
    """Mark all notifications as read"""
    mark_all_notifications_read()
    return {"message": "All notifications marked as read"}
