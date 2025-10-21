"""Notification system for the Worklog Manager."""

import logging
import threading
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum

from core.settings import NotificationSettings, NotificationType


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Notification:
    """Represents a notification."""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    timestamp: datetime = None
    action_callback: Optional[Callable] = None
    action_text: Optional[str] = None
    auto_dismiss_seconds: int = 0  # 0 = no auto dismiss
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class NotificationManager:
    """Manages notifications and reminders for the worklog application."""
    
    def __init__(self, settings: NotificationSettings, parent_window: tk.Tk = None):
        """Initialize notification manager.
        
        Args:
            settings: Notification settings
            parent_window: Parent tkinter window for dialogs
        """
        self.settings = settings
        self.parent_window = parent_window
        self.logger = logging.getLogger(__name__)
        
        # Notification state
        self.active_notifications: Dict[str, Notification] = {}
        self.notification_history: List[Notification] = []
        self.max_history = 100
        
        # Timing and callbacks
        self.timer_thread: Optional[threading.Thread] = None
        self.running = False
        self.check_interval = 60  # Check every minute
        
        # Callback registrations
        self.worklog_manager = None
        
        # Sound system (optional)
        self.sound_enabled = settings.sound_notifications
        
        # Start notification monitoring
        self.start_monitoring()
    
    def set_worklog_manager(self, manager):
        """Set the worklog manager reference for status checking.
        
        Args:
            manager: WorklogManager instance
        """
        self.worklog_manager = manager
    
    def start_monitoring(self):
        """Start the notification monitoring thread."""
        if not self.running:
            self.running = True
            self.timer_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.timer_thread.start()
            self.logger.info("Notification monitoring started")
    
    def stop_monitoring(self):
        """Stop the notification monitoring."""
        self.running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        self.logger.info("Notification monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs in background thread."""
        last_break_check = datetime.now()
        last_work_reminder = None
        last_overtime_check = datetime.now()
        
        while self.running:
            try:
                current_time = datetime.now()
                
                if not self.settings.enabled:
                    time.sleep(self.check_interval)
                    continue
                
                # Check work start reminders
                if self.settings.work_start_reminder:
                    self._check_work_start_reminder(current_time)
                
                # Check break reminders (every 5 minutes)
                if (current_time - last_break_check).seconds >= 300:
                    if self.settings.break_reminders:
                        self._check_break_reminders(current_time)
                    last_break_check = current_time
                
                # Check end of day reminder
                if self.settings.end_day_reminder:
                    self._check_end_day_reminder(current_time)
                
                # Check overtime warnings (every 10 minutes)
                if (current_time - last_overtime_check).seconds >= 600:
                    if self.settings.overtime_warnings:
                        self._check_overtime_warnings(current_time)
                    last_overtime_check = current_time
                
                # Clean up old notifications
                self._cleanup_notifications()
                
            except Exception as e:
                self.logger.error(f"Notification monitoring error: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_work_start_reminder(self, current_time: datetime):
        """Check if work start reminder should be shown."""
        if not self.worklog_manager:
            return
        
        # Parse work start time
        try:
            start_hour, start_minute = map(int, self.settings.work_start_time.split(':'))
            work_start = current_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            
            # Check if it's work start time and not already working
            time_diff = (current_time - work_start).total_seconds()
            
            # Remind if within 5 minutes of start time and not working
            if 0 <= time_diff <= 300:  # 0-5 minutes after start time
                from data.models import WorklogState
                if self.worklog_manager.get_current_state() == WorklogState.NOT_STARTED:
                    self.show_notification(
                        NotificationType.WORK_REMINDER,
                        "Work Day Start",
                        f"It's {self.settings.work_start_time}! Time to start your work day.",
                        NotificationPriority.NORMAL,
                        action_text="Start Day",
                        action_callback=self._start_day_callback,
                        auto_dismiss_seconds=300
                    )
        except ValueError:
            self.logger.error(f"Invalid work start time format: {self.settings.work_start_time}")
    
    def _check_break_reminders(self, current_time: datetime):
        """Check if break reminders should be shown."""
        if not self.worklog_manager:
            return
        
        from data.models import WorklogState
        
        # Only remind if actively working
        if self.worklog_manager.get_current_state() != WorklogState.WORKING:
            return
        
        # Check how long user has been working continuously
        calculations = self.worklog_manager.get_current_calculations()
        current_session_minutes = calculations.current_session_minutes
        
        # Remind about long work sessions
        if (current_session_minutes >= self.settings.long_work_warning and 
            current_session_minutes % self.settings.break_reminder_interval == 0):
            
            hours = current_session_minutes // 60
            minutes = current_session_minutes % 60
            
            self.show_notification(
                NotificationType.BREAK_REMINDER,
                "Break Reminder",
                f"You've been working for {hours}h {minutes}m continuously. Consider taking a break!",
                NotificationPriority.NORMAL,
                action_text="Take Break",
                action_callback=self._take_break_callback,
                auto_dismiss_seconds=180
            )
    
    def _check_end_day_reminder(self, current_time: datetime):
        """Check if end of day reminder should be shown."""
        if not self.worklog_manager:
            return
        
        try:
            end_hour, end_minute = map(int, self.settings.end_day_time.split(':'))
            end_time = current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            
            # Check if it's end time and still working
            time_diff = (current_time - end_time).total_seconds()
            
            if 0 <= time_diff <= 300:  # 0-5 minutes after end time
                from data.models import WorklogState
                state = self.worklog_manager.get_current_state()
                if state in [WorklogState.WORKING, WorklogState.ON_BREAK]:
                    calculations = self.worklog_manager.get_current_calculations()
                    work_hours = calculations.total_work_minutes / 60
                    
                    self.show_notification(
                        NotificationType.DAY_END_REMINDER,
                        "End of Work Day",
                        f"It's {self.settings.end_day_time}! You've worked {work_hours:.1f} hours today. Consider ending your work day.",
                        NotificationPriority.NORMAL,
                        action_text="End Day",
                        action_callback=self._end_day_callback,
                        auto_dismiss_seconds=600
                    )
        except ValueError:
            self.logger.error(f"Invalid end day time format: {self.settings.end_day_time}")
    
    def _check_overtime_warnings(self, current_time: datetime):
        """Check if overtime warnings should be shown."""
        if not self.worklog_manager:
            return
        
        from data.models import WorklogState
        
        # Only check if working
        state = self.worklog_manager.get_current_state()
        if state not in [WorklogState.WORKING, WorklogState.ON_BREAK]:
            return
        
        calculations = self.worklog_manager.get_current_calculations()
        work_hours = calculations.total_work_minutes / 60
        
        # Get overtime threshold from work norms
        # For now, use 8 hours as default (this should come from settings)
        overtime_threshold = 8.0
        warning_threshold = overtime_threshold - self.settings.overtime_warning_threshold
        
        # Warn if approaching overtime
        if work_hours >= warning_threshold and work_hours < overtime_threshold:
            remaining = overtime_threshold - work_hours
            self.show_notification(
                NotificationType.OVERTIME_WARNING,
                "Overtime Warning",
                f"You have {remaining:.1f} hours until overtime. Current work time: {work_hours:.1f} hours",
                NotificationPriority.HIGH,
                auto_dismiss_seconds=300
            )
        
        # Critical warning if in overtime
        elif work_hours >= overtime_threshold:
            overtime = work_hours - overtime_threshold
            self.show_notification(
                NotificationType.OVERTIME_WARNING,
                "Overtime Alert",
                f"You are now in overtime! Extra hours worked: {overtime:.1f}",
                NotificationPriority.CRITICAL,
                auto_dismiss_seconds=0  # Don't auto-dismiss
            )
    
    def show_notification(self, notification_type: NotificationType, title: str, 
                         message: str, priority: NotificationPriority = NotificationPriority.NORMAL,
                         action_text: str = None, action_callback: Callable = None,
                         auto_dismiss_seconds: int = 0) -> str:
        """Show a notification to the user.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            action_text: Text for action button (optional)
            action_callback: Callback for action button (optional)
            auto_dismiss_seconds: Auto dismiss after X seconds (0 = no auto dismiss)
            
        Returns:
            Notification ID
        """
        if not self.settings.enabled:
            return ""
        
        # Create notification
        notification_id = f"{notification_type.value}_{int(time.time())}"
        notification = Notification(
            id=notification_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            action_callback=action_callback,
            action_text=action_text,
            auto_dismiss_seconds=auto_dismiss_seconds
        )
        
        # Check for duplicate notifications (same type within 5 minutes)
        now = datetime.now()
        for existing in self.active_notifications.values():
            if (existing.type == notification_type and 
                (now - existing.timestamp).total_seconds() < 300):
                return existing.id  # Don't show duplicate
        
        # Store notification
        self.active_notifications[notification_id] = notification
        self.notification_history.append(notification)
        
        # Trim history
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
        
        # Show notification based on system settings
        if self.settings.system_notifications:
            self._show_system_notification(notification)
        else:
            self._show_dialog_notification(notification)
        
        # Play sound if enabled
        if self.sound_enabled:
            self._play_notification_sound(priority)
        
        # Schedule auto-dismiss if specified
        if auto_dismiss_seconds > 0:
            threading.Timer(
                auto_dismiss_seconds, 
                lambda: self.dismiss_notification(notification_id)
            ).start()
        
        self.logger.info(f"Notification shown: {title}")
        return notification_id
    
    def _show_system_notification(self, notification: Notification):
        """Show system tray notification (Windows/Linux/Mac)."""
        try:
            # Try to use plyer for cross-platform notifications
            try:
                from plyer import notification as plyer_notification
                plyer_notification.notify(
                    title=notification.title,
                    message=notification.message,
                    timeout=10 if notification.auto_dismiss_seconds == 0 else notification.auto_dismiss_seconds
                )
                return
            except ImportError:
                pass
            
            # Fallback to tkinter messagebox (will show as dialog)
            self._show_dialog_notification(notification)
            
        except Exception as e:
            self.logger.error(f"Failed to show system notification: {e}")
            # Fallback to dialog
            self._show_dialog_notification(notification)
    
    def _show_dialog_notification(self, notification: Notification):
        """Show notification as tkinter dialog."""
        if not self.parent_window:
            return
        
        try:
            # Use appropriate messagebox based on priority
            if notification.priority == NotificationPriority.CRITICAL:
                icon = 'error'
            elif notification.priority == NotificationPriority.HIGH:
                icon = 'warning'
            else:
                icon = 'info'
            
            # Show notification in main thread
            def show_dialog():
                if notification.action_callback and notification.action_text:
                    result = messagebox.askyesno(
                        notification.title,
                        f"{notification.message}\n\nWould you like to {notification.action_text.lower()}?",
                        icon=icon
                    )
                    if result and notification.action_callback:
                        try:
                            notification.action_callback()
                        except Exception as e:
                            self.logger.error(f"Notification action callback failed: {e}")
                else:
                    messagebox.showinfo(notification.title, notification.message, icon=icon)
            
            # Schedule to run in main thread
            if self.parent_window:
                self.parent_window.after(0, show_dialog)
                
        except Exception as e:
            self.logger.error(f"Failed to show dialog notification: {e}")
    
    def _play_notification_sound(self, priority: NotificationPriority):
        """Play notification sound based on priority."""
        if not self.sound_enabled:
            return
        
        try:
            # System beep for now - could be enhanced with actual sound files
            if priority == NotificationPriority.CRITICAL:
                # Multiple beeps for critical
                for _ in range(3):
                    print('\a')  # System beep
                    time.sleep(0.2)
            elif priority == NotificationPriority.HIGH:
                # Two beeps for high priority
                for _ in range(2):
                    print('\a')
                    time.sleep(0.1)
            else:
                # Single beep for normal/low
                print('\a')
        except Exception as e:
            self.logger.error(f"Failed to play notification sound: {e}")
    
    def dismiss_notification(self, notification_id: str):
        """Dismiss an active notification.
        
        Args:
            notification_id: ID of notification to dismiss
        """
        if notification_id in self.active_notifications:
            del self.active_notifications[notification_id]
    
    def _cleanup_notifications(self):
        """Clean up old notifications."""
        now = datetime.now()
        to_remove = []
        
        for notification_id, notification in self.active_notifications.items():
            # Remove notifications older than 1 hour
            if (now - notification.timestamp).total_seconds() > 3600:
                to_remove.append(notification_id)
        
        for notification_id in to_remove:
            del self.active_notifications[notification_id]
    
    def get_active_notifications(self) -> List[Notification]:
        """Get list of active notifications.
        
        Returns:
            List of active notifications
        """
        return list(self.active_notifications.values())
    
    def get_notification_history(self, limit: int = 50) -> List[Notification]:
        """Get notification history.
        
        Args:
            limit: Maximum number of notifications to return
            
        Returns:
            List of recent notifications
        """
        return self.notification_history[-limit:]
    
    def update_settings(self, settings: NotificationSettings):
        """Update notification settings.
        
        Args:
            settings: New notification settings
        """
        self.settings = settings
        self.sound_enabled = settings.sound_notifications
        self.logger.info("Notification settings updated")
    
    # Callback methods for notification actions
    def _start_day_callback(self):
        """Callback for start day notification action."""
        if self.worklog_manager:
            try:
                self.worklog_manager.start_day()
                self.logger.info("Work day started from notification")
            except Exception as e:
                self.logger.error(f"Failed to start day from notification: {e}")
    
    def _take_break_callback(self):
        """Callback for take break notification action."""
        if self.worklog_manager:
            try:
                from data.models import BreakType
                self.worklog_manager.stop_work(BreakType.GENERAL)
                self.logger.info("Break started from notification")
            except Exception as e:
                self.logger.error(f"Failed to start break from notification: {e}")
    
    def _end_day_callback(self):
        """Callback for end day notification action."""
        if self.worklog_manager:
            try:
                self.worklog_manager.end_day()
                self.logger.info("Work day ended from notification")
            except Exception as e:
                self.logger.error(f"Failed to end day from notification: {e}")
    
    def test_notifications(self):
        """Test all notification types for debugging."""
        test_notifications = [
            (NotificationType.WORK_REMINDER, "Test Work Reminder", "This is a test work reminder."),
            (NotificationType.BREAK_REMINDER, "Test Break Reminder", "This is a test break reminder."),
            (NotificationType.OVERTIME_WARNING, "Test Overtime Warning", "This is a test overtime warning."),
            (NotificationType.DAY_END_REMINDER, "Test Day End", "This is a test day end reminder."),
        ]
        
        for i, (notif_type, title, message) in enumerate(test_notifications):
            # Stagger the notifications
            threading.Timer(i * 2, lambda t=notif_type, tt=title, m=message: self.show_notification(
                t, tt, m, NotificationPriority.NORMAL, auto_dismiss_seconds=5
            )).start()
        
        self.logger.info("Test notifications scheduled")