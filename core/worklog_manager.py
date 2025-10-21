"""Core worklog management class."""

import logging
from datetime import datetime, date
from typing import Optional, Callable, List
import threading
import time

from data.database import Database
from data.models import (
    WorkSession, ActionLog, BreakPeriod, TimeCalculation,
    WorklogState, ActionType, BreakType
)
from core.time_calculator import TimeCalculator
from core.action_history import ActionHistory


class WorklogManager:
    """Main business logic class for managing work sessions."""
    
    def __init__(self, db_path: str = "worklog.db", settings_manager=None):
        """Initialize the worklog manager.
        
        Args:
            db_path: Path to the SQLite database file
            settings_manager: Settings manager instance for configuration
        """
        self.db = Database(db_path)
        self.time_calculator = TimeCalculator(settings_manager=settings_manager)
        self.action_history = ActionHistory()
        self.logger = logging.getLogger(__name__)
        
        # Current session state
        self.current_session: Optional[WorkSession] = None
        self.current_state: WorklogState = WorklogState.NOT_STARTED
        self.current_break_id: Optional[int] = None
        
        # Timer thread for real-time updates
        self.timer_thread: Optional[threading.Thread] = None
        self.timer_running = False
        self.timer_callback: Optional[Callable] = None
        
        # Load or create today's session
        self._load_todays_session()
    
    def _load_todays_session(self):
        """Load or create today's work session."""
        today = date.today().isoformat()
        
        session = self.db.get_session_by_date(today)
        if session:
            self.current_session = session
            self.current_state = session.status
            self.logger.info(f"Loaded existing session for {today}")
        else:
            # Create new session for today
            session_id = self.db.create_session(today)
            self.current_session = self.db.get_session_by_date(today)
            self.current_state = WorklogState.NOT_STARTED
            self.logger.info(f"Created new session for {today}")
        
        # Start timer if needed
        if self.current_state == WorklogState.WORKING:
            self.start_timer()
    
    def set_timer_callback(self, callback: Callable):
        """Set callback function for timer updates.
        
        Args:
            callback: Function to call on timer updates
        """
        self.timer_callback = callback
    
    def start_timer(self):
        """Start the real-time timer thread."""
        if not self.timer_running:
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer_thread.start()
            self.logger.debug("Timer started")
    
    def stop_timer(self):
        """Stop the real-time timer thread."""
        self.timer_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        self.logger.debug("Timer stopped")
    
    def _timer_loop(self):
        """Timer loop that runs in background thread."""
        while self.timer_running:
            try:
                if self.timer_callback and self.current_state == WorklogState.WORKING:
                    self.timer_callback()
                time.sleep(1)  # Update every second
            except Exception as e:
                self.logger.error(f"Timer loop error: {e}")
                break
    
    def get_current_calculations(self) -> TimeCalculation:
        """Get current time calculations for the session.
        
        Returns:
            TimeCalculation object with current metrics
        """
        if not self.current_session:
            return TimeCalculation()
        
        actions = self.db.get_session_actions(self.current_session.id)
        breaks = self.db.get_session_breaks(self.current_session.id)
        
        return self.time_calculator.calculate_all_times(actions, breaks)
    
    def start_day(self) -> bool:
        """Start the work day.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_state != WorklogState.NOT_STARTED:
                self.logger.warning(f"Cannot start day in state {self.current_state}")
                return False
            
            if not self.current_session:
                self.logger.error("No current session available")
                return False
            
            # Record state before action
            state_before = self.current_state
            
            # Log action
            timestamp = datetime.now().isoformat()
            self.db.log_action(
                self.current_session.id,
                ActionType.START_DAY,
                timestamp
            )
            
            # Update session
            self.db.update_session(
                self.current_session.id,
                start_time=timestamp,
                status=WorklogState.WORKING.value
            )
            
            # Update state
            self.current_state = WorklogState.WORKING
            self.start_timer()
            
            # Record action in history
            self._record_action_in_history(
                ActionType.START_DAY, 
                state_before, 
                self.current_state
            )
            
            self.logger.info("Work day started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start day: {e}")
            return False
    
    def stop_work(self, break_type: BreakType = BreakType.GENERAL) -> bool:
        """Stop work and start a break.
        
        Args:
            break_type: Type of break being taken
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_state != WorklogState.WORKING:
                self.logger.warning(f"Cannot stop work in state {self.current_state}")
                return False
            
            if not self.current_session:
                self.logger.error("No current session available")
                return False
            
            # Record state before action
            state_before = self.current_state
            
            timestamp = datetime.now().isoformat()
            
            # Log stop action
            self.db.log_action(
                self.current_session.id,
                ActionType.STOP,
                timestamp,
                break_type=break_type
            )
            
            # Create break period
            self.current_break_id = self.db.create_break_period(
                self.current_session.id,
                break_type,
                timestamp
            )
            
            # Update state
            self.current_state = WorklogState.ON_BREAK
            
            # Record action in history
            self._record_action_in_history(
                ActionType.STOP,
                state_before,
                self.current_state,
                break_data={
                    'break_type': break_type.value,
                    'break_id': self.current_break_id,
                    'start_time': timestamp
                }
            )
            
            self.logger.info(f"Work stopped for {break_type.value} break")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop work: {e}")
            return False
    
    def continue_work(self) -> bool:
        """Continue work after a break.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_state != WorklogState.ON_BREAK:
                self.logger.warning(f"Cannot continue work in state {self.current_state}")
                return False
            
            if not self.current_session:
                self.logger.error("No current session available")
                return False
            
            # Record state before action
            state_before = self.current_state
            
            timestamp = datetime.now().isoformat()
            
            # End current break period
            break_info = {}
            if self.current_break_id:
                breaks = self.db.get_session_breaks(self.current_session.id)
                current_break = next(
                    (b for b in breaks if b.id == self.current_break_id), None
                )

                if current_break:
                    break_info = {
                        'break_id': self.current_break_id,
                        'break_type': current_break.break_type.value,
                        'start_time': current_break.start_time,
                        'end_time': timestamp
                    }

                duration_minutes = 0
                duration_seconds = 0
                if current_break and current_break.start_time:
                    start_time = self.time_calculator.parse_time(current_break.start_time)
                    end_time = self.time_calculator.parse_time(timestamp)
                    duration_seconds = max(0, int((end_time - start_time).total_seconds()))
                    duration_minutes = max(0, int(duration_seconds / 60))
                
                self.db.end_break_period(self.current_break_id, timestamp, duration_minutes)

                if break_info:
                    break_info['duration_seconds'] = duration_seconds
                    break_info['duration_minutes'] = duration_minutes

                self.current_break_id = None
            
            # Log continue action
            self.db.log_action(
                self.current_session.id,
                ActionType.CONTINUE,
                timestamp
            )
            
            # Update state
            self.current_state = WorklogState.WORKING
            
            # Record action in history
            self._record_action_in_history(
                ActionType.CONTINUE,
                state_before,
                self.current_state,
                break_data=break_info if break_info else None
            )
            
            self.logger.info("Work continued after break")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to continue work: {e}")
            return False
    
    def end_day(self) -> bool:
        """End the work day.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.current_state not in [WorklogState.WORKING, WorklogState.ON_BREAK]:
                self.logger.warning(f"Cannot end day in state {self.current_state}")
                return False
            
            if not self.current_session:
                self.logger.error("No current session available")
                return False
            
            # Record state before action
            state_before = self.current_state
            
            timestamp = datetime.now().isoformat()
            
            # If on break, end the break first
            if self.current_state == WorklogState.ON_BREAK and self.current_break_id:
                breaks = self.db.get_session_breaks(self.current_session.id)
                current_break = next(
                    (b for b in breaks if b.id == self.current_break_id), None
                )
                
                if current_break and current_break.start_time:
                    start_time = self.time_calculator.parse_time(current_break.start_time)
                    end_time = self.time_calculator.parse_time(timestamp)
                    duration = int((end_time - start_time).total_seconds() / 60)
                    
                    self.db.end_break_period(self.current_break_id, timestamp, duration)
                
                self.current_break_id = None
            
            # Log end day action
            self.db.log_action(
                self.current_session.id,
                ActionType.END_DAY,
                timestamp
            )
            
            # Calculate final times
            calculations = self.get_current_calculations()
            
            # Update session with final data
            self.db.update_session(
                self.current_session.id,
                end_time=timestamp,
                total_work_minutes=calculations.total_work_minutes,
                total_break_minutes=calculations.total_break_minutes,
                productive_minutes=calculations.productive_minutes,
                overtime_minutes=calculations.overtime_minutes,
                status=WorklogState.DAY_ENDED.value
            )
            
            # Update state
            self.current_state = WorklogState.DAY_ENDED
            self.stop_timer()
            
            # Record action in history
            self._record_action_in_history(
                ActionType.END_DAY,
                state_before,
                self.current_state
            )
            
            self.logger.info("Work day ended")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to end day: {e}")
            return False

    def reset_day(self) -> bool:
        """Reset the current day, clearing all data and starting fresh.
        
        This will:
        - Delete all work sessions for today
        - Clear all break periods for today  
        - Clear action logs for today
        - Reset state to NOT_STARTED
        - Clear action history
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_session:
                self.logger.warning("No current session to reset")
                return False
            
            session_id = self.current_session.id
            today = date.today().isoformat()
            
            # Stop any running timers
            self.stop_timer()
            
            # Record state before reset for logging
            state_before = self.current_state
            
            # Clear all data for today's session
            self.db.delete_session_breaks(session_id)
            self.db.delete_session_actions(session_id) 
            self.db.delete_session(session_id)
            
            # Clear action history
            self.action_history.clear_history()
            
            # Reset current state
            self.current_session = None
            self.current_state = WorklogState.NOT_STARTED
            self.current_break_id = None
            
            # Create fresh session for today
            session_id = self.db.create_session(today)
            self.current_session = self.db.get_session_by_date(today)
            
            self.logger.info(f"Successfully reset day - cleared all data for {today}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset day: {e}")
            return False
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Check if an action can be performed in the current state.
        
        Args:
            action_type: Action to check
            
        Returns:
            True if action is allowed, False otherwise
        """
        valid_transitions = {
            WorklogState.NOT_STARTED: [ActionType.START_DAY],
            WorklogState.WORKING: [ActionType.STOP, ActionType.END_DAY],
            WorklogState.ON_BREAK: [ActionType.CONTINUE, ActionType.END_DAY],
            WorklogState.DAY_ENDED: []
        }
        
        return action_type in valid_transitions.get(self.current_state, [])
    
    def get_current_state(self) -> WorklogState:
        """Get the current worklog state.
        
        Returns:
            Current WorklogState
        """
        return self.current_state
    
    def get_current_session(self) -> Optional[WorkSession]:
        """Get the current work session.
        
        Returns:
            Current WorkSession or None
        """
        return self.current_session
    
    def refresh_session(self):
        """Refresh the current session from database."""
        if self.current_session:
            updated_session = self.db.get_session_by_date(self.current_session.date)
            if updated_session:
                self.current_session = updated_session
    
    def get_action_history(self) -> ActionHistory:
        """Get the action history manager.
        
        Returns:
            ActionHistory instance
        """
        return self.action_history
    
    def revoke_action(self, action_id: str) -> bool:
        """Revoke a specific action and restore previous state.
        
        Args:
            action_id: ID of the action to revoke
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the action to revoke
            action = self.action_history.get_action_by_id(action_id)
            if not action:
                self.logger.error(f"Action not found: {action_id}")
                return False
            
            # Check if action can be revoked
            if not self.action_history.can_revoke_action(action_id):
                self.logger.error(f"Action cannot be revoked: {action_id}")
                return False
            
            # Get state before the action
            state_before = action.state_before
            session_data_before = action.session_data_before
            
            # Mark action as revoked in history
            self.action_history.revoke_action(action_id, "User requested revoke")
            
            # Mark corresponding database action as revoked
            if self.current_session:
                db_actions = self.db.get_session_actions(self.current_session.id)
                
                # Find the corresponding database action by timestamp and type
                for db_action in db_actions:
                    if (db_action.action_type == action.action_type and 
                        abs((self.time_calculator.parse_time(db_action.timestamp) - 
                             action.timestamp).total_seconds()) < 5):  # Within 5 seconds
                        self.db.revoke_action(db_action.id)
                        break
            
            # Restore state
            self._restore_state_from_action(action)
            
            self.logger.info(f"Successfully revoked action: {action.action_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke action {action_id}: {e}")
            return False
    
    def _restore_state_from_action(self, action):
        """Restore system state from a revoked action.
        
        Args:
            action: ActionSnapshot to restore from
        """
        # Restore worklog state
        old_state = self.current_state
        self.current_state = action.state_before
        
        # Handle specific action types
        if action.action_type == ActionType.START_DAY:
            # Revert start day - reset session start time
            if self.current_session:
                self.db.update_session(
                    self.current_session.id,
                    start_time=None,
                    status=WorklogState.NOT_STARTED.value
                )
                self.stop_timer()
                
        elif action.action_type == ActionType.END_DAY:
            # Revert end day - clear end time and restore working/break state
            if self.current_session:
                # Determine correct state from action history
                actions = self.action_history.get_revokable_actions()
                if len(actions) > 1:  # There should be previous actions
                    previous_action = actions[1]  # Second item (first is the one we just revoked)
                    restore_state = previous_action.state_after
                else:
                    restore_state = WorklogState.WORKING
                
                self.current_state = restore_state
                
                self.db.update_session(
                    self.current_session.id,
                    end_time=None,
                    status=restore_state.value
                )
                
                if restore_state == WorklogState.WORKING:
                    self.start_timer()
                    
        elif action.action_type == ActionType.STOP:
            # Revert stop - remove break period and restore working state
            break_id = None
            if action.break_data:
                break_id = action.break_data.get('break_id')

            if break_id is not None and self.current_session:
                try:
                    self.db.delete_break_period(int(break_id))
                except Exception as error:
                    self.logger.error(f"Failed to delete break period {break_id}: {error}")

            self.current_break_id = None

            if self.current_session:
                status_value = self.current_state.value if hasattr(self.current_state, 'value') else str(self.current_state)
                self.db.update_session(
                    self.current_session.id,
                    status=status_value
                )

        elif action.action_type == ActionType.CONTINUE:
            # Revert continue - restore break state and reopen the break period
            break_id = None
            if action.break_data:
                break_id = action.break_data.get('break_id')

            if break_id is not None and self.current_session:
                try:
                    reopened = self.db.reopen_break_period(int(break_id))
                    if reopened:
                        self.current_break_id = int(break_id)
                except Exception as error:
                    self.logger.error(f"Failed to reopen break period {break_id}: {error}")

            if self.current_session:
                status_value = self.current_state.value if hasattr(self.current_state, 'value') else str(self.current_state)
                self.db.update_session(
                    self.current_session.id,
                    status=status_value
                )
        
        self.logger.info(f"State restored from {old_state} to {self.current_state}")
        self.refresh_session()
    
    def _record_action_in_history(self, action_type: ActionType, state_before: WorklogState,
                                 state_after: WorklogState, break_data: dict = None):
        """Record an action in the action history.
        
        Args:
            action_type: Type of action performed
            state_before: State before the action
            state_after: State after the action
            break_data: Break-related data if applicable
        """
        session_data_before = {}
        session_data_after = {}
        
        if self.current_session:
            session_data_before = {
                'session_id': self.current_session.id,
                'start_time': self.current_session.start_time,
                'end_time': self.current_session.end_time,
                'status': self.current_session.status.value if hasattr(self.current_session.status, 'value') else str(self.current_session.status)
            }
            
            # Refresh session to get updated data
            self.refresh_session()
            
            session_data_after = {
                'session_id': self.current_session.id,
                'start_time': self.current_session.start_time,
                'end_time': self.current_session.end_time,
                'status': self.current_session.status.value if hasattr(self.current_session.status, 'value') else str(self.current_session.status)
            }
        
        self.action_history.record_action(
            action_type=action_type,
            state_before=state_before,
            state_after=state_after,
            session_data_before=session_data_before,
            session_data_after=session_data_after,
            break_data=break_data or {}
        )