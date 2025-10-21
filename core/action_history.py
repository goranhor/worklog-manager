"""Action history management for the Worklog Manager application."""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from data.models import WorklogState, ActionType, BreakType
from utils.datetime_compat import datetime_fromisoformat


@dataclass
class ActionSnapshot:
    """Represents a snapshot of system state before an action."""
    id: str
    action_type: ActionType
    timestamp: datetime
    state_before: WorklogState
    state_after: WorklogState
    session_data_before: Optional[Dict[str, Any]] = None
    session_data_after: Optional[Dict[str, Any]] = None
    break_data: Optional[Dict[str, Any]] = None
    revoked: bool = False
    revoke_timestamp: Optional[datetime] = None
    notes: Optional[str] = None


class ActionHistory:
    """Manages action history and revoke functionality."""
    
    def __init__(self, max_history: int = 100):
        """Initialize action history manager.
        
        Args:
            max_history: Maximum number of actions to keep in history
        """
        self.max_history = max_history
        self.actions: List[ActionSnapshot] = []
        self.logger = logging.getLogger(__name__)
    
    def record_action(self, action_type: ActionType, state_before: WorklogState,
                     state_after: WorklogState, session_data_before: Dict[str, Any] = None,
                     session_data_after: Dict[str, Any] = None,
                     break_data: Dict[str, Any] = None, notes: str = None) -> str:
        """Record a new action in history.
        
        Args:
            action_type: Type of action performed
            state_before: State before the action
            state_after: State after the action
            session_data_before: Session data before action
            session_data_after: Session data after action
            break_data: Break-related data if applicable
            notes: Additional notes about the action
            
        Returns:
            Unique ID of the recorded action
        """
        action_id = str(uuid.uuid4())
        
        snapshot = ActionSnapshot(
            id=action_id,
            action_type=action_type,
            timestamp=datetime.now(),
            state_before=state_before,
            state_after=state_after,
            session_data_before=session_data_before or {},
            session_data_after=session_data_after or {},
            break_data=break_data or {},
            notes=notes
        )
        
        self.actions.append(snapshot)
        
        # Maintain history size limit
        if len(self.actions) > self.max_history:
            removed = self.actions.pop(0)
            self.logger.debug(f"Removed old action from history: {removed.id}")
        
        self.logger.info(f"Recorded action: {action_type.value} (ID: {action_id})")
        return action_id
    
    def get_revokable_actions(self) -> List[ActionSnapshot]:
        """Get list of actions that can be revoked.
        
        Returns:
            List of non-revoked actions in reverse chronological order
        """
        revokable = [action for action in self.actions if not action.revoked]
        return list(reversed(revokable))  # Most recent first
    
    def get_last_action(self) -> Optional[ActionSnapshot]:
        """Get the most recent non-revoked action.
        
        Returns:
            Last action or None if no actions available
        """
        revokable = self.get_revokable_actions()
        return revokable[0] if revokable else None
    
    def get_action_by_id(self, action_id: str) -> Optional[ActionSnapshot]:
        """Get an action by its ID.
        
        Args:
            action_id: Unique ID of the action
            
        Returns:
            ActionSnapshot or None if not found
        """
        for action in self.actions:
            if action.id == action_id:
                return action
        return None
    
    def revoke_action(self, action_id: str, notes: str = None) -> bool:
        """Mark an action as revoked.
        
        Args:
            action_id: ID of the action to revoke
            notes: Optional notes about the revoke operation
            
        Returns:
            True if action was successfully revoked
        """
        action = self.get_action_by_id(action_id)
        if not action:
            self.logger.error(f"Action not found for revoke: {action_id}")
            return False
        
        if action.revoked:
            self.logger.warning(f"Action already revoked: {action_id}")
            return False
        
        action.revoked = True
        action.revoke_timestamp = datetime.now()
        if notes:
            action.notes = f"{action.notes or ''}\nRevoked: {notes}".strip()
        
        self.logger.info(f"Revoked action: {action.action_type.value} (ID: {action_id})")
        return True
    
    def can_revoke_action(self, action_id: str) -> bool:
        """Check if an action can be revoked.
        
        Args:
            action_id: ID of the action to check
            
        Returns:
            True if action can be revoked
        """
        action = self.get_action_by_id(action_id)
        if not action or action.revoked:
            return False
        
        # Additional business logic for revoke validation
        revokable_actions = self.get_revokable_actions()
        
        # Can only revoke actions from the end of the sequence
        # (to maintain state consistency)
        for i, revokable_action in enumerate(revokable_actions):
            if revokable_action.id == action_id:
                # Can revoke if it's one of the last few actions
                return i < 5  # Allow revoking last 5 actions
        
        return False
    
    def get_actions_after(self, action_id: str) -> List[ActionSnapshot]:
        """Get all actions that occurred after a specific action.
        
        Args:
            action_id: ID of the reference action
            
        Returns:
            List of actions that occurred after the reference action
        """
        reference_action = self.get_action_by_id(action_id)
        if not reference_action:
            return []
        
        return [
            action for action in self.actions
            if (action.timestamp > reference_action.timestamp and 
                not action.revoked)
        ]
    
    def get_state_before_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get the system state before a specific action.
        
        Args:
            action_id: ID of the action
            
        Returns:
            Dictionary containing state information
        """
        action = self.get_action_by_id(action_id)
        if not action:
            return None
        
        return {
            'worklog_state': action.state_before,
            'session_data': action.session_data_before,
            'break_data': action.break_data
        }
    
    def get_history_summary(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get a summary of recent actions for display.
        
        Args:
            limit: Maximum number of actions to include
            
        Returns:
            List of action summaries
        """
        recent_actions = self.get_revokable_actions()[:limit]
        
        summaries = []
        for action in recent_actions:
            summary = {
                'id': action.id,
                'action_type': action.action_type.value,
                'timestamp': action.timestamp.strftime('%H:%M:%S'),
                'description': self._get_action_description(action),
                'can_revoke': self.can_revoke_action(action.id),
                'revoked': action.revoked
            }
            summaries.append(summary)
        
        return summaries
    
    def _get_action_description(self, action: ActionSnapshot) -> str:
        """Get a human-readable description of an action.
        
        Args:
            action: ActionSnapshot to describe
            
        Returns:
            Human-readable description
        """
        descriptions = {
            ActionType.START_DAY: "Started work day",
            ActionType.END_DAY: "Ended work day",
            ActionType.STOP: f"Stopped work ({action.break_data.get('break_type', 'unknown')} break)",
            ActionType.CONTINUE: "Continued work",
        }
        
        base_description = descriptions.get(action.action_type, action.action_type.value)
        
        if action.revoked:
            return f"{base_description} (REVOKED)"
        
        return base_description
    
    def clear_history(self):
        """Clear all action history."""
        self.actions.clear()
        self.logger.info("Action history cleared")
    
    def export_history(self) -> List[Dict[str, Any]]:
        """Export action history for backup or analysis.
        
        Returns:
            List of action data dictionaries
        """
        return [asdict(action) for action in self.actions]
    
    def import_history(self, history_data: List[Dict[str, Any]]):
        """Import action history from backup.
        
        Args:
            history_data: List of action data dictionaries
        """
        try:
            imported_actions = []
            for data in history_data:
                # Convert string enums back to enum objects
                data['action_type'] = ActionType(data['action_type'])
                data['state_before'] = WorklogState(data['state_before'])
                data['state_after'] = WorklogState(data['state_after'])
                
                # Convert timestamp strings back to datetime
                data['timestamp'] = datetime_fromisoformat(data['timestamp'])
                if data.get('revoke_timestamp'):
                    data['revoke_timestamp'] = datetime_fromisoformat(data['revoke_timestamp'])
                
                action = ActionSnapshot(**data)
                imported_actions.append(action)
            
            self.actions = imported_actions
            self.logger.info(f"Imported {len(imported_actions)} actions from history")
            
        except Exception as e:
            self.logger.error(f"Failed to import history: {e}")
            raise

    def clear_history(self):
        """Clear all action history.
        
        This is typically used when resetting a day or starting fresh.
        """
        actions_count = len(self.actions)
        self.actions.clear()
        self.logger.info(f"Cleared action history - removed {actions_count} actions")