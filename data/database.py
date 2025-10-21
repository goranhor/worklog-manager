"""Database operations for the Worklog Manager application."""

import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from data.models import WorkSession, ActionLog, BreakPeriod, WorklogState, ActionType, BreakType
from utils.datetime_compat import datetime_fromisoformat


class Database:
    """Database manager for SQLite operations."""
    
    def __init__(self, db_path: str = "worklog.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        try:
            with self.get_connection() as conn:
                self._create_tables(conn)
            self.logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create all required database tables."""
        
        # Work sessions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                start_time TEXT,
                end_time TEXT,
                total_work_minutes INTEGER DEFAULT 0,
                total_break_minutes INTEGER DEFAULT 0,
                productive_minutes INTEGER DEFAULT 0,
                overtime_minutes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'not_started',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Action log table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS action_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                break_type TEXT,
                notes TEXT,
                revoked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES work_sessions (id)
            )
        """)
        
        # Break periods table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS break_periods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                break_type TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_minutes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES work_sessions (id)
            )
        """)
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON work_sessions(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_actions_session ON action_log(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_breaks_session ON break_periods(session_id)")
        
        conn.commit()
    
    def create_session(self, date: str) -> int:
        """Create a new work session for the given date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            ID of the created session
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO work_sessions (date) VALUES (?)",
                (date,)
            )
            conn.commit()
            session_id = cursor.lastrowid
            self.logger.info(f"Created new session {session_id} for date {date}")
            return session_id
    
    def get_session_by_date(self, date: str) -> Optional[WorkSession]:
        """Get work session for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            WorkSession object or None if not found
        """
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM work_sessions WHERE date = ?",
                (date,)
            ).fetchone()
            
            if row:
                return WorkSession(
                    id=row['id'],
                    date=row['date'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    total_work_minutes=row['total_work_minutes'],
                    total_break_minutes=row['total_break_minutes'],
                    productive_minutes=row['productive_minutes'],
                    overtime_minutes=row['overtime_minutes'],
                    status=WorklogState(row['status']),
                    created_at=datetime_fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime_fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            return None
    
    def update_session(self, session_id: int, **kwargs):
        """Update session with new data.
        
        Args:
            session_id: ID of the session to update
            **kwargs: Fields to update
        """
        if not kwargs:
            return
        
        # Add updated timestamp
        kwargs['updated_at'] = datetime.now().isoformat()
        
        # Build UPDATE query
        fields = ', '.join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values()) + [session_id]
        
        with self.get_connection() as conn:
            conn.execute(
                f"UPDATE work_sessions SET {fields} WHERE id = ?",
                values
            )
            conn.commit()
            self.logger.debug(f"Updated session {session_id} with {kwargs}")
    
    def log_action(self, session_id: int, action_type: ActionType, 
                   timestamp: str, break_type: Optional[BreakType] = None,
                   notes: Optional[str] = None) -> int:
        """Log a user action.
        
        Args:
            session_id: ID of the work session
            action_type: Type of action performed
            timestamp: When the action occurred
            break_type: Type of break (if applicable)
            notes: Additional notes
            
        Returns:
            ID of the logged action
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO action_log 
                   (session_id, action_type, timestamp, break_type, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, action_type.value, timestamp, 
                 break_type.value if break_type else None, notes)
            )
            conn.commit()
            action_id = cursor.lastrowid
            self.logger.info(f"Logged action {action_type.value} for session {session_id}")
            return action_id
    
    def get_session_actions(self, session_id: int) -> List[ActionLog]:
        """Get all actions for a session.
        
        Args:
            session_id: ID of the work session
            
        Returns:
            List of ActionLog objects
        """
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM action_log 
                   WHERE session_id = ? AND revoked = FALSE
                   ORDER BY created_at""",
                (session_id,)
            ).fetchall()
            
            actions = []
            for row in rows:
                actions.append(ActionLog(
                    id=row['id'],
                    session_id=row['session_id'],
                    action_type=ActionType(row['action_type']),
                    timestamp=row['timestamp'],
                    break_type=BreakType(row['break_type']) if row['break_type'] else None,
                    notes=row['notes'],
                    revoked=bool(row['revoked']),
                    created_at=datetime_fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            return actions
    
    def create_break_period(self, session_id: int, break_type: BreakType, 
                          start_time: str) -> int:
        """Create a new break period.
        
        Args:
            session_id: ID of the work session
            break_type: Type of break
            start_time: When the break started
            
        Returns:
            ID of the created break period
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO break_periods (session_id, break_type, start_time) VALUES (?, ?, ?)",
                (session_id, break_type.value, start_time)
            )
            conn.commit()
            break_id = cursor.lastrowid
            self.logger.info(f"Created break period {break_id} for session {session_id}")
            return break_id
    
    def end_break_period(self, break_id: int, end_time: str, duration_minutes: int):
        """End a break period.
        
        Args:
            break_id: ID of the break period
            end_time: When the break ended
            duration_minutes: Duration of the break in minutes
        """
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE break_periods SET end_time = ?, duration_minutes = ? WHERE id = ?",
                (end_time, duration_minutes, break_id)
            )
            conn.commit()
            self.logger.info(f"Ended break period {break_id}")

    def delete_break_period(self, break_id: int) -> bool:
        """Delete a break period entry.

        Args:
            break_id: ID of the break period to remove

        Returns:
            True if a break period was deleted
        """
        with self.get_connection() as conn:
            result = conn.execute(
                "DELETE FROM break_periods WHERE id = ?",
                (break_id,)
            )
            conn.commit()
            deleted = result.rowcount > 0
            if deleted:
                self.logger.info(f"Deleted break period {break_id}")
            else:
                self.logger.warning(f"No break period found with ID {break_id}")
            return deleted

    def reopen_break_period(self, break_id: int) -> bool:
        """Reopen a break period by clearing its end time and duration.

        Args:
            break_id: ID of the break period to reopen

        Returns:
            True if the break period was updated
        """
        with self.get_connection() as conn:
            result = conn.execute(
                "UPDATE break_periods SET end_time = NULL, duration_minutes = NULL WHERE id = ?",
                (break_id,)
            )
            conn.commit()
            updated = result.rowcount > 0
            if updated:
                self.logger.info(f"Reopened break period {break_id}")
            else:
                self.logger.warning(f"Failed to reopen break period {break_id} - not found")
            return updated
    
    def get_session_breaks(self, session_id: int) -> List[BreakPeriod]:
        """Get all break periods for a session.
        
        Args:
            session_id: ID of the work session
            
        Returns:
            List of BreakPeriod objects
        """
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM break_periods WHERE session_id = ? ORDER BY created_at",
                (session_id,)
            ).fetchall()
            
            breaks = []
            for row in rows:
                breaks.append(BreakPeriod(
                    id=row['id'],
                    session_id=row['session_id'],
                    break_type=BreakType(row['break_type']),
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    duration_minutes=row['duration_minutes'],
                    created_at=datetime_fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            return breaks
    
    def revoke_action(self, action_id: int):
        """Mark an action as revoked.
        
        Args:
            action_id: ID of the action to revoke
        """
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE action_log SET revoked = TRUE WHERE id = ?",
                (action_id,)
            )
            conn.commit()
            self.logger.info(f"Revoked action {action_id}")
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database.
        
        Args:
            backup_path: Path where backup should be saved
        """
        try:
            with self.get_connection() as source:
                backup = sqlite3.connect(backup_path)
                source.backup(backup)
                backup.close()
            self.logger.info(f"Database backed up to {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            raise

    def delete_session_breaks(self, session_id: int):
        """Delete all break periods for a session.
        
        Args:
            session_id: ID of the session
        """
        with self.get_connection() as conn:
            result = conn.execute(
                "DELETE FROM break_periods WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()
            deleted_count = result.rowcount
            self.logger.info(f"Deleted {deleted_count} break periods for session {session_id}")

    def delete_session_actions(self, session_id: int):
        """Delete all action logs for a session.
        
        Args:
            session_id: ID of the session
        """
        with self.get_connection() as conn:
            result = conn.execute(
                "DELETE FROM action_log WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()
            deleted_count = result.rowcount
            self.logger.info(f"Deleted {deleted_count} action logs for session {session_id}")

    def delete_session(self, session_id: int):
        """Delete a work session.
        
        Args:
            session_id: ID of the session to delete
        """
        with self.get_connection() as conn:
            result = conn.execute(
                "DELETE FROM work_sessions WHERE id = ?",
                (session_id,)
            )
            conn.commit()
            if result.rowcount > 0:
                self.logger.info(f"Deleted session {session_id}")
            else:
                self.logger.warning(f"No session found with ID {session_id}")