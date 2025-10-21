"""Timer display component for real-time time tracking."""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import logging

from data.models import TimeCalculation, WorklogState
from core.time_calculator import TimeCalculator


class TimerDisplay(ttk.Frame):
    """Component for displaying real-time work time information."""
    
    def __init__(self, parent, settings_manager=None):
        """Initialize the timer display.
        
        Args:
            parent: Parent widget
            settings_manager: Settings manager for work norms
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.settings_manager = settings_manager
        self.time_calculator = TimeCalculator(settings_manager)
        
        zero_time = self.time_calculator.format_duration_with_seconds(0)
        norm_time = self.time_calculator.format_duration_with_seconds(
            self.time_calculator.WORK_NORM_MINUTES * 60
        )

        # Create variables for time displays
        self.current_session_var = tk.StringVar(value=zero_time)
        self.total_work_var = tk.StringVar(value=zero_time)
        self.break_time_var = tk.StringVar(value=zero_time)
        self.productive_time_var = tk.StringVar(value=zero_time)
        self.remaining_var = tk.StringVar(value=norm_time)
        self.overtime_var = tk.StringVar(value=zero_time)

        self._create_widgets()
    
    def update_settings_manager(self, settings_manager):
        """Update the settings manager and time calculator."""
        self.settings_manager = settings_manager
        self.time_calculator = TimeCalculator(settings_manager)
    
    def _create_widgets(self):
        """Create and layout the timer display widgets."""
        # Main frame with border
        main_frame = ttk.LabelFrame(self, text="Time Summary", padding="10")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a grid layout for time displays
        row = 0
        
        # Current session time (highlighted)
        current_frame = tk.Frame(main_frame, bg="#E8F4FD", relief="ridge", bd=1)
        current_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        current_frame.columnconfigure(1, weight=1)
        
        tk.Label(current_frame, text="Current Session:", 
                font=("Arial", 10, "bold"), bg="#E8F4FD").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.current_session_label = tk.Label(current_frame, textvariable=self.current_session_var,
                                            font=("Arial", 12, "bold"), fg="#0066CC", bg="#E8F4FD")
        self.current_session_label.grid(row=0, column=1, sticky="e", padx=5, pady=5)
        
        row += 1
        
        # Total work time
        tk.Label(main_frame, text="Total Work Time:", 
                font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=2)
        
        self.total_work_label = tk.Label(main_frame, textvariable=self.total_work_var,
                                       font=("Arial", 9, "bold"))
        self.total_work_label.grid(row=row, column=1, sticky="e", pady=2)
        
        row += 1
        
        # Break time
        tk.Label(main_frame, text="Break Time:", 
                font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=2)
        
        self.break_time_label = tk.Label(main_frame, textvariable=self.break_time_var,
                                       font=("Arial", 9, "bold"))
        self.break_time_label.grid(row=row, column=1, sticky="e", pady=2)
        
        row += 1
        
        # Productive time
        tk.Label(main_frame, text="Productive Time:", 
                font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=2)
        
        self.productive_time_label = tk.Label(main_frame, textvariable=self.productive_time_var,
                                            font=("Arial", 9, "bold"))
        self.productive_time_label.grid(row=row, column=1, sticky="e", pady=2)
        
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, 
                                                           sticky="ew", pady=5)
        row += 1
        
        # Remaining time
        tk.Label(main_frame, text="Remaining:", 
                font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=2)
        
        self.remaining_label = tk.Label(main_frame, textvariable=self.remaining_var,
                                      font=("Arial", 9, "bold"))
        self.remaining_label.grid(row=row, column=1, sticky="e", pady=2)
        
        row += 1
        
        # Overtime
        tk.Label(main_frame, text="Overtime:", 
                font=("Arial", 9)).grid(row=row, column=0, sticky="w", pady=2)
        
        self.overtime_label = tk.Label(main_frame, textvariable=self.overtime_var,
                                     font=("Arial", 9, "bold"))
        self.overtime_label.grid(row=row, column=1, sticky="e", pady=2)
        
        # Configure column weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def update_display(self, calculations: TimeCalculation, current_session_seconds: int = 0):
        """Update the timer display with new calculations.
        
        Args:
            calculations: TimeCalculation object with current metrics
            current_session_seconds: Current session time in seconds
        """
        try:
            # Update current session time
            current_session_str = self.time_calculator.format_duration_with_seconds(current_session_seconds)
            self.current_session_var.set(current_session_str)
            
            # Update work times
            self.total_work_var.set(
                self.time_calculator.format_duration_with_seconds(calculations.total_work_seconds)
            )
            self.break_time_var.set(
                self.time_calculator.format_duration_with_seconds(calculations.total_break_seconds)
            )
            self.productive_time_var.set(
                self.time_calculator.format_duration_with_seconds(calculations.productive_seconds)
            )
            self.remaining_var.set(
                self.time_calculator.format_duration_with_seconds(calculations.remaining_seconds)
            )
            self.overtime_var.set(
                self.time_calculator.format_duration_with_seconds(calculations.overtime_seconds)
            )
            
            # Update colors based on status
            self._update_colors(calculations)
            
        except Exception as e:
            self.logger.error(f"Failed to update display: {e}")
    
    def _update_colors(self, calculations: TimeCalculation):
        """Update label colors based on work status.
        
        Args:
            calculations: TimeCalculation object
        """
        # Color scheme
        normal_color = "#000000"  # Black
        warning_color = "#FF8C00"  # Orange
        overtime_color = "#DC143C"  # Red
        good_color = "#006400"  # Green
        
        # Productive time color
        if calculations.is_overtime:
            self.productive_time_label.config(fg=overtime_color)
            self.overtime_label.config(fg=overtime_color)
        elif calculations.productive_minutes >= calculations.work_norm_minutes * 0.9:  # 90% of norm
            self.productive_time_label.config(fg=good_color)
            self.overtime_label.config(fg=normal_color)
        elif calculations.productive_minutes >= calculations.work_norm_minutes * 0.7:  # 70% of norm
            self.productive_time_label.config(fg=warning_color)
            self.overtime_label.config(fg=normal_color)
        else:
            self.productive_time_label.config(fg=normal_color)
            self.overtime_label.config(fg=normal_color)
        
        # Remaining time color
        if calculations.remaining_minutes == 0:
            self.remaining_label.config(fg=good_color)
        elif calculations.remaining_minutes <= 60:  # Less than 1 hour remaining
            self.remaining_label.config(fg=warning_color)
        else:
            self.remaining_label.config(fg=normal_color)
    
    def reset_display(self):
        """Reset all displays to zero."""
        zero_time = self.time_calculator.format_duration_with_seconds(0)
        norm_time = self.time_calculator.format_duration_with_seconds(
            self.time_calculator.WORK_NORM_MINUTES * 60
        )

        self.current_session_var.set(zero_time)
        self.total_work_var.set(zero_time)
        self.break_time_var.set(zero_time)
        self.productive_time_var.set(zero_time)
        self.remaining_var.set(norm_time)
        self.overtime_var.set(zero_time)
        
        # Reset colors
        normal_color = "#000000"
        self.productive_time_label.config(fg=normal_color)
        self.remaining_label.config(fg=normal_color)
        self.overtime_label.config(fg=normal_color)