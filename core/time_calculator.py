"""Time calculation utilities for the Worklog Manager."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from data.models import ActionLog, BreakPeriod, TimeCalculation, ActionType, WorklogState
from utils.datetime_compat import datetime_fromisoformat


class TimeCalculator:
    """Handles all time-related calculations for work sessions."""
    
    def __init__(self, settings_manager=None):
        self.logger = logging.getLogger(__name__)
        self.settings_manager = settings_manager
        self._cached_work_norm_minutes = None
    
    @property
    def WORK_NORM_MINUTES(self):
        """Get work norm minutes from settings or use default."""
        if self.settings_manager:
            try:
                daily_hours = self.settings_manager.settings.work_norms.daily_work_hours
                return int(daily_hours * 60)
            except:
                pass
        return 450  # 7.5 hours default
    
    @staticmethod
    def parse_time(time_str: str) -> datetime:
        """Parse time string to datetime object.
        
        Args:
            time_str: Time in ISO format (YYYY-MM-DD HH:MM:SS)
            
        Returns:
            datetime object
        """
        return datetime_fromisoformat(time_str)
    
    @staticmethod
    def format_time(dt: datetime) -> str:
        """Format datetime to string.
        
        Args:
            dt: datetime object
            
        Returns:
            Time in ISO format
        """
        return dt.isoformat()
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """Format duration in minutes to HH:MM:SS format."""
        if minutes < 0:
            return "00:00:00"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}:00"
    
    @staticmethod
    def format_duration_with_seconds(total_seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS format.
        
        Args:
            total_seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if total_seconds < 0:
            return "00:00:00"
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def calculate_work_time(self, actions: List[ActionLog]) -> int:
        """Calculate total work time from the action log in seconds."""
        total_seconds = 0
        current_start = None

        for action in actions:
            timestamp = self.parse_time(action.timestamp)

            if action.action_type == ActionType.START_DAY:
                current_start = timestamp
            elif action.action_type == ActionType.STOP and current_start:
                duration = timestamp - current_start
                total_seconds += int(duration.total_seconds())
                current_start = None
            elif action.action_type == ActionType.CONTINUE:
                current_start = timestamp
            elif action.action_type == ActionType.END_DAY and current_start:
                duration = timestamp - current_start
                total_seconds += int(duration.total_seconds())
                current_start = None

        return total_seconds
    
    def calculate_current_session_time(self, actions: List[ActionLog]) -> int:
        """Calculate current active session time in seconds.
        
        Args:
            actions: List of ActionLog objects
            
        Returns:
            Current session time in seconds
        """
        if not actions:
            return 0
        
        # Find the last action that started a work period
        last_start = None
        for action in reversed(actions):
            if action.action_type in [ActionType.START_DAY, ActionType.CONTINUE]:
                last_start = self.parse_time(action.timestamp)
                break
            elif action.action_type in [ActionType.STOP, ActionType.END_DAY]:
                # Session is not currently active
                return 0
        
        if last_start:
            current_time = datetime.now()
            duration = current_time - last_start
            return int(duration.total_seconds())
        
        return 0
    
    def calculate_break_time(self, break_periods: List[BreakPeriod]) -> int:
        """Calculate total break time in seconds."""
        total_seconds = 0

        for break_period in break_periods:
            if break_period.start_time and break_period.end_time:
                start = self.parse_time(break_period.start_time)
                end = self.parse_time(break_period.end_time)
                duration = end - start
                total_seconds += max(0, int(duration.total_seconds()))
            elif break_period.duration_minutes is not None:
                total_seconds += max(0, int(break_period.duration_minutes * 60))

        return total_seconds
    
    def calculate_all_times(self, actions: List[ActionLog], 
                          break_periods: List[BreakPeriod]) -> TimeCalculation:
        """Calculate all time metrics for a work session.
        
        Args:
            actions: List of ActionLog objects
            break_periods: List of BreakPeriod objects
            
        Returns:
            TimeCalculation object with all metrics
        """
        total_work_seconds = self.calculate_work_time(actions)
        total_break_seconds = self.calculate_break_time(break_periods)
        current_session_seconds = self.calculate_current_session_time(actions)
        
        # Productive time is work time (breaks are not deducted from work time)
        productive_seconds = total_work_seconds
        
        # Calculate overtime/deficit
        work_norm_seconds = self.WORK_NORM_MINUTES * 60

        if productive_seconds > work_norm_seconds:
            overtime_seconds = productive_seconds - work_norm_seconds
            deficit_seconds = 0
            remaining_seconds = 0
        else:
            overtime_seconds = 0
            deficit_seconds = work_norm_seconds - productive_seconds
            remaining_seconds = deficit_seconds

        total_work_minutes = total_work_seconds // 60
        total_break_minutes = total_break_seconds // 60
        productive_minutes = productive_seconds // 60
        overtime_minutes = overtime_seconds // 60
        deficit_minutes = deficit_seconds // 60
        remaining_minutes = remaining_seconds // 60
        
        return TimeCalculation(
            total_work_seconds=total_work_seconds,
            total_break_seconds=total_break_seconds,
            productive_seconds=productive_seconds,
            overtime_seconds=overtime_seconds,
            deficit_seconds=deficit_seconds,
            remaining_seconds=remaining_seconds,
            current_session_seconds=current_session_seconds,
            work_norm_seconds=work_norm_seconds,
            total_work_minutes=total_work_minutes,
            total_break_minutes=total_break_minutes,
            productive_minutes=productive_minutes,
            overtime_minutes=overtime_minutes,
            deficit_minutes=deficit_minutes,
            remaining_minutes=remaining_minutes,
            current_session_minutes=current_session_seconds // 60,
            is_overtime=overtime_seconds > 0,
            work_norm_minutes=self.WORK_NORM_MINUTES
        )
    
    def get_work_state_from_actions(self, actions: List[ActionLog]) -> WorklogState:
        """Determine current work state from action history.
        
        Args:
            actions: List of ActionLog objects
            
        Returns:
            Current WorklogState
        """
        if not actions:
            return WorklogState.NOT_STARTED
        
        last_action = actions[-1]
        
        if last_action.action_type == ActionType.START_DAY:
            return WorklogState.WORKING
        elif last_action.action_type == ActionType.STOP:
            return WorklogState.ON_BREAK
        elif last_action.action_type == ActionType.CONTINUE:
            return WorklogState.WORKING
        elif last_action.action_type == ActionType.END_DAY:
            return WorklogState.DAY_ENDED
        
        return WorklogState.NOT_STARTED