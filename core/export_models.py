"""Export models and data structures for the Worklog Manager."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from data.models import WorkSession, BreakPeriod, ActionLog


class ExportFormat(Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"


class ReportType(Enum):
    """Types of reports available."""
    DAILY_SUMMARY = "daily_summary"
    DETAILED_LOG = "detailed_log"
    BREAK_ANALYSIS = "break_analysis"
    PRODUCTIVITY_REPORT = "productivity_report"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"


@dataclass
class DateRange:
    """Represents a date range for filtering exports."""
    start_date: date
    end_date: date
    
    def __post_init__(self):
        """Validate date range."""
        if self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
    
    def contains(self, check_date: date) -> bool:
        """Check if a date falls within this range."""
        return self.start_date <= check_date <= self.end_date
    
    def days_count(self) -> int:
        """Get the number of days in this range."""
        return (self.end_date - self.start_date).days + 1


@dataclass
class ExportOptions:
    """Configuration options for exports."""
    format: ExportFormat
    report_type: ReportType
    date_range: DateRange
    include_breaks: bool = True
    include_actions: bool = True
    include_analytics: bool = True
    group_by_date: bool = True
    filename: Optional[str] = None


@dataclass
class DailyStats:
    """Statistics for a single day."""
    date: date
    total_work_minutes: int
    total_break_minutes: int
    productive_minutes: int
    overtime_minutes: int
    breaks_count: int
    coffee_breaks: int
    lunch_breaks: int
    general_breaks: int
    sessions_count: int
    first_start: Optional[datetime] = None
    last_end: Optional[datetime] = None
    
    @property
    def work_hours(self) -> float:
        """Get work time in hours."""
        return self.total_work_minutes / 60.0
    
    @property
    def break_hours(self) -> float:
        """Get break time in hours."""
        return self.total_break_minutes / 60.0
    
    @property
    def productivity_percentage(self) -> float:
        """Calculate productivity percentage."""
        total_time = self.total_work_minutes + self.total_break_minutes
        if total_time == 0:
            return 0.0
        return (self.productive_minutes / total_time) * 100


@dataclass
class WeeklyStats:
    """Statistics for a week."""
    week_start: date
    week_end: date
    daily_stats: List[DailyStats] = field(default_factory=list)
    
    @property
    def total_work_minutes(self) -> int:
        """Total work minutes for the week."""
        return sum(day.total_work_minutes for day in self.daily_stats)
    
    @property
    def total_break_minutes(self) -> int:
        """Total break minutes for the week."""
        return sum(day.total_break_minutes for day in self.daily_stats)
    
    @property
    def average_daily_work(self) -> float:
        """Average daily work time in minutes."""
        work_days = [day for day in self.daily_stats if day.total_work_minutes > 0]
        if not work_days:
            return 0.0
        return sum(day.total_work_minutes for day in work_days) / len(work_days)
    
    @property
    def productivity_percentage(self) -> float:
        """Average productivity percentage for the week."""
        productive_days = [day for day in self.daily_stats if day.total_work_minutes > 0]
        if not productive_days:
            return 0.0
        return sum(day.productivity_percentage for day in productive_days) / len(productive_days)


@dataclass
class ExportData:
    """Container for all export data."""
    options: ExportOptions
    sessions: List[WorkSession] = field(default_factory=list)
    breaks: List[BreakPeriod] = field(default_factory=list)
    actions: List[ActionLog] = field(default_factory=list)
    daily_stats: List[DailyStats] = field(default_factory=list)
    weekly_stats: List[WeeklyStats] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set metadata after initialization."""
        self.metadata = {
            'export_date': datetime.now().isoformat(),
            'date_range': {
                'start': self.options.date_range.start_date.isoformat(),
                'end': self.options.date_range.end_date.isoformat(),
                'days_count': self.options.date_range.days_count()
            },
            'format': self.options.format.value,
            'report_type': self.options.report_type.value,
            'total_sessions': len(self.sessions),
            'total_breaks': len(self.breaks),
            'total_actions': len(self.actions)
        }


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    filepath: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set result metadata."""
        self.metadata['timestamp'] = datetime.now().isoformat()
        if self.filepath:
            import os
            self.metadata['file_size'] = os.path.getsize(self.filepath) if os.path.exists(self.filepath) else 0