"""Data models for the Worklog Manager application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class WorklogState(Enum):
    """Enumeration of possible worklog states."""
    NOT_STARTED = "not_started"
    WORKING = "working"
    ON_BREAK = "on_break"
    DAY_ENDED = "day_ended"


class ActionType(Enum):
    """Enumeration of possible user actions."""
    START_DAY = "start_day"
    END_DAY = "end_day"
    STOP = "stop"
    CONTINUE = "continue"
    REVOKE_START = "revoke_start"
    REVOKE_END = "revoke_end"
    REVOKE_STOP = "revoke_stop"
    REVOKE_CONTINUE = "revoke_continue"


class BreakType(Enum):
    """Enumeration of break types."""
    LUNCH = "lunch"
    COFFEE = "coffee"
    GENERAL = "general"


@dataclass
class WorkSession:
    """Data model for a work session."""
    id: Optional[int] = None
    date: str = ""
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_work_minutes: int = 0
    total_break_minutes: int = 0
    productive_minutes: int = 0
    overtime_minutes: int = 0
    status: WorklogState = WorklogState.NOT_STARTED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ActionLog:
    """Data model for action logging."""
    id: Optional[int] = None
    session_id: int = 0
    action_type: ActionType = ActionType.START_DAY
    timestamp: str = ""
    break_type: Optional[BreakType] = None
    notes: Optional[str] = None
    revoked: bool = False
    created_at: Optional[datetime] = None


@dataclass
class BreakPeriod:
    """Data model for break periods."""
    id: Optional[int] = None
    session_id: int = 0
    break_type: BreakType = BreakType.GENERAL
    start_time: str = ""
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class TimeCalculation:
    """Data model for time calculation results."""
    total_work_seconds: int = 0
    total_break_seconds: int = 0
    productive_seconds: int = 0
    overtime_seconds: int = 0
    deficit_seconds: int = 0
    remaining_seconds: int = 0
    current_session_seconds: int = 0
    work_norm_seconds: int = 450 * 60
    total_work_minutes: int = 0
    total_break_minutes: int = 0
    productive_minutes: int = 0
    overtime_minutes: int = 0
    deficit_minutes: int = 0
    remaining_minutes: int = 0
    current_session_minutes: int = 0
    is_overtime: bool = False
    work_norm_minutes: int = 450  # 7.5 hours