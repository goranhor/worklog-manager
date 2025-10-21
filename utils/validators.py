"""Validation utilities for the Worklog Manager."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from data.models import WorklogState, ActionType, BreakType, WorkSession
from core.action_history import ActionHistory, ActionSnapshot
from utils.datetime_compat import datetime_fromisoformat


class WorklogValidator:
    """Validator for worklog operations and state transitions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_state_transition(self, current_state: WorklogState, 
                                action_type: ActionType) -> Tuple[bool, str]:
        """Validate if a state transition is allowed.
        
        Args:
            current_state: Current worklog state
            action_type: Proposed action
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_transitions = {
            WorklogState.NOT_STARTED: [ActionType.START_DAY],
            WorklogState.WORKING: [ActionType.STOP, ActionType.END_DAY],
            WorklogState.ON_BREAK: [ActionType.CONTINUE, ActionType.END_DAY],
            WorklogState.DAY_ENDED: []
        }
        
        allowed_actions = valid_transitions.get(current_state, [])
        
        if action_type not in allowed_actions:
            return False, f"Cannot perform {action_type.value} while in {current_state.value} state"
        
        return True, ""
    
    def validate_session_data(self, session: WorkSession) -> Tuple[bool, str]:
        """Validate session data integrity.
        
        Args:
            session: WorkSession to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not session:
            return False, "Session is None"
        
        if not session.date:
            return False, "Session date is missing"
        
        # Validate date format
        try:
            datetime_fromisoformat(session.date)
        except ValueError:
            return False, f"Invalid date format: {session.date}"
        
        # Validate times if present
        if session.start_time:
            try:
                datetime_fromisoformat(session.start_time)
            except ValueError:
                return False, f"Invalid start time format: {session.start_time}"
        
        if session.end_time:
            try:
                end_time = datetime_fromisoformat(session.end_time)
                if session.start_time:
                    start_time = datetime_fromisoformat(session.start_time)
                    if end_time < start_time:
                        return False, "End time cannot be before start time"
            except ValueError:
                return False, f"Invalid end time format: {session.end_time}"
        
        # Validate numeric fields
        numeric_fields = [
            session.total_work_minutes,
            session.total_break_minutes,
            session.productive_minutes,
            session.overtime_minutes
        ]
        
        for field in numeric_fields:
            if field < 0:
                return False, "Time values cannot be negative"
        
        return True, ""
    
    def validate_break_type(self, break_type: BreakType) -> Tuple[bool, str]:
        """Validate break type.
        
        Args:
            break_type: Break type to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(break_type, BreakType):
            return False, f"Invalid break type: {break_type}"
        
        return True, ""
    
    def validate_revoke_operation(self, action_history: ActionHistory, 
                                action_id: str) -> Tuple[bool, str]:
        """Validate if a revoke operation is allowed.
        
        Args:
            action_history: ActionHistory instance
            action_id: ID of action to revoke
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if action exists
        action = action_history.get_action_by_id(action_id)
        if not action:
            return False, "Action not found"
        
        # Check if already revoked
        if action.revoked:
            return False, "Action has already been revoked"
        
        # Check if action can be revoked based on business rules
        if not action_history.can_revoke_action(action_id):
            return False, "Action cannot be revoked (too old or dependent actions exist)"
        
        # Validate action timestamp is reasonable
        time_diff = datetime.now() - action.timestamp
        if time_diff > timedelta(hours=24):
            return False, "Cannot revoke actions older than 24 hours"
        
        return True, ""
    
    def validate_work_time_limits(self, total_minutes: int) -> Tuple[bool, str]:
        """Validate work time against reasonable limits.
        
        Args:
            total_minutes: Total work time in minutes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Maximum reasonable work day (16 hours)
        MAX_WORK_MINUTES = 16 * 60
        
        if total_minutes < 0:
            return False, "Work time cannot be negative"
        
        if total_minutes > MAX_WORK_MINUTES:
            return False, f"Work time exceeds maximum limit ({MAX_WORK_MINUTES // 60} hours)"
        
        return True, ""
    
    def validate_break_duration(self, duration_minutes: int, 
                              break_type: BreakType) -> Tuple[bool, str]:
        """Validate break duration is reasonable.
        
        Args:
            duration_minutes: Break duration in minutes
            break_type: Type of break
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if duration_minutes < 0:
            return False, "Break duration cannot be negative"
        
        # Set reasonable limits based on break type
        max_durations = {
            BreakType.COFFEE: 30,      # 30 minutes max for coffee
            BreakType.LUNCH: 120,      # 2 hours max for lunch
            BreakType.GENERAL: 240     # 4 hours max for general breaks
        }
        
        max_duration = max_durations.get(break_type, 240)
        
        if duration_minutes > max_duration:
            return False, f"{break_type.value.title()} break exceeds maximum duration ({max_duration} minutes)"
        
        return True, ""
    
    def validate_date_range(self, start_date: str, end_date: str) -> Tuple[bool, str]:
        """Validate date range for exports or queries.
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            start = datetime_fromisoformat(start_date)
            end = datetime_fromisoformat(end_date)
        except ValueError as e:
            return False, f"Invalid date format: {e}"
        
        if start > end:
            return False, "Start date cannot be after end date"
        
        # Limit range to reasonable period (1 year)
        if (end - start).days > 365:
            return False, "Date range cannot exceed 365 days"
        
        # Check future dates
        today = datetime.now().date()
        if start.date() > today:
            return False, "Start date cannot be in the future"
        
        return True, ""
    
    def validate_action_sequence(self, actions: List[ActionSnapshot]) -> Tuple[bool, str]:
        """Validate that a sequence of actions is logical.
        
        Args:
            actions: List of actions in chronological order
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not actions:
            return True, ""
        
        previous_state = WorklogState.NOT_STARTED
        
        for i, action in enumerate(actions):
            if action.revoked:
                continue
            
            # Validate state transition
            is_valid, error = self.validate_state_transition(previous_state, action.action_type)
            if not is_valid:
                return False, f"Invalid transition at action {i + 1}: {error}"
            
            previous_state = action.state_after
        
        return True, ""


class InputValidator:
    """Validator for user input data."""
    
    @staticmethod
    def validate_time_string(time_str: str) -> Tuple[bool, str]:
        """Validate time string format.
        
        Args:
            time_str: Time string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not time_str:
            return False, "Time string is empty"
        
        try:
            datetime_fromisoformat(time_str)
            return True, ""
        except ValueError:
            return False, f"Invalid time format: {time_str}"
    
    @staticmethod
    def validate_numeric_input(value: str, field_name: str, 
                             min_val: float = 0, max_val: float = None) -> Tuple[bool, str]:
        """Validate numeric input.
        
        Args:
            value: String value to validate
            field_name: Name of the field for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            num_val = float(value)
        except ValueError:
            return False, f"{field_name} must be a valid number"
        
        if num_val < min_val:
            return False, f"{field_name} cannot be less than {min_val}"
        
        if max_val is not None and num_val > max_val:
            return False, f"{field_name} cannot be greater than {max_val}"
        
        return True, ""
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """Validate file path for exports.
        
        Args:
            file_path: File path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "File path is empty"
        
        # Basic path validation
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in file_path:
                return False, f"File path contains invalid character: {char}"
        
        return True, ""