"""Enhanced break management component."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any
import logging

from data.models import BreakType, BreakPeriod
from core.time_calculator import TimeCalculator


class BreakTracker(ttk.Frame):
    """Component for tracking and displaying break information."""
    
    def __init__(self, parent):
        """Initialize the break tracker.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.time_calculator = TimeCalculator()
        
        self._create_widgets()
        self._break_periods: List[BreakPeriod] = []
    
    def _create_widgets(self):
        """Create and layout widgets."""
        # Main frame
        main_frame = ttk.LabelFrame(self, text="Break Summary", padding="5")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Break summary grid
        self._create_summary_grid(main_frame)
        
        # Recent breaks list
        self._create_recent_breaks(main_frame)
    
    def _create_summary_grid(self, parent):
        """Create break summary grid.
        
        Args:
            parent: Parent widget
        """
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill="x", pady=(0, 10))
        
        # Headers
        tk.Label(summary_frame, text="Break Type", font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 20))
        tk.Label(summary_frame, text="Count", font=("Arial", 9, "bold")).grid(
            row=0, column=1, sticky="w", padx=(0, 20))
        tk.Label(summary_frame, text="Total Time", font=("Arial", 9, "bold")).grid(
            row=0, column=2, sticky="w")
        
        # Break type rows
        zero_time = self.time_calculator.format_duration_with_seconds(0)
        self.lunch_count_var = tk.StringVar(value="0")
        self.lunch_time_var = tk.StringVar(value=zero_time)
        self.coffee_count_var = tk.StringVar(value="0")
        self.coffee_time_var = tk.StringVar(value=zero_time)
        self.general_count_var = tk.StringVar(value="0")
        self.general_time_var = tk.StringVar(value=zero_time)
        
        # Lunch breaks
        lunch_frame = tk.Frame(summary_frame, bg="#FFE4B5", relief="ridge", bd=1)
        lunch_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=1)
        lunch_frame.columnconfigure(2, weight=1)
        
        tk.Label(lunch_frame, text="[L] Lunch", bg="#FFE4B5").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(lunch_frame, textvariable=self.lunch_count_var, bg="#FFE4B5").grid(row=0, column=1, padx=20, pady=2)
        tk.Label(lunch_frame, textvariable=self.lunch_time_var, bg="#FFE4B5").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        
        # Coffee breaks
        coffee_frame = tk.Frame(summary_frame, bg="#D2B48C", relief="ridge", bd=1)
        coffee_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=1)
        coffee_frame.columnconfigure(2, weight=1)
        
        tk.Label(coffee_frame, text="[C] Coffee", bg="#D2B48C").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(coffee_frame, textvariable=self.coffee_count_var, bg="#D2B48C").grid(row=0, column=1, padx=20, pady=2)
        tk.Label(coffee_frame, textvariable=self.coffee_time_var, bg="#D2B48C").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        
        # General breaks
        general_frame = tk.Frame(summary_frame, bg="#F0F0F0", relief="ridge", bd=1)
        general_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=1)
        general_frame.columnconfigure(2, weight=1)
        
        tk.Label(general_frame, text="[B] General", bg="#F0F0F0").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(general_frame, textvariable=self.general_count_var, bg="#F0F0F0").grid(row=0, column=1, padx=20, pady=2)
        tk.Label(general_frame, textvariable=self.general_time_var, bg="#F0F0F0").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        
        summary_frame.columnconfigure(0, weight=1)
    
    def _create_recent_breaks(self, parent):
        """Create recent breaks list.
        
        Args:
            parent: Parent widget
        """
        recent_frame = ttk.LabelFrame(parent, text="Recent Breaks", padding="5")
        recent_frame.pack(fill="both", expand=True)
        
        # Create listbox with scrollbar
        listbox_frame = ttk.Frame(recent_frame)
        listbox_frame.pack(fill="both", expand=True)
        
        self.breaks_listbox = tk.Listbox(listbox_frame, height=4, font=("Arial", 8))
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.breaks_listbox.yview)
        self.breaks_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.breaks_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_breaks(self, break_periods: List[BreakPeriod]):
        """Update break display with new data.
        
        Args:
            break_periods: List of BreakPeriod objects
        """
        self._break_periods = break_periods
        self._update_summary()
        self._update_recent_list()
    
    def _update_summary(self):
        """Update the break summary counts and times."""
        # Count breaks by type
        lunch_breaks = [b for b in self._break_periods if b.break_type == BreakType.LUNCH]
        coffee_breaks = [b for b in self._break_periods if b.break_type == BreakType.COFFEE]
        general_breaks = [b for b in self._break_periods if b.break_type == BreakType.GENERAL]
        
        # Calculate total times (seconds precision)
        lunch_time = sum(self._break_duration_seconds(b) for b in lunch_breaks)
        coffee_time = sum(self._break_duration_seconds(b) for b in coffee_breaks)
        general_time = sum(self._break_duration_seconds(b) for b in general_breaks)
        
        # Update variables
        self.lunch_count_var.set(str(len(lunch_breaks)))
        self.lunch_time_var.set(self._format_seconds(lunch_time))
        
        self.coffee_count_var.set(str(len(coffee_breaks)))
        self.coffee_time_var.set(self._format_seconds(coffee_time))
        
        self.general_count_var.set(str(len(general_breaks)))
        self.general_time_var.set(self._format_seconds(general_time))
    
    def _update_recent_list(self):
        """Update the recent breaks list."""
        self.breaks_listbox.delete(0, tk.END)
        
        if not self._break_periods:
            self.breaks_listbox.insert(tk.END, "No breaks taken today")
            return
        
        # Show most recent breaks first
        recent_breaks = sorted(self._break_periods, 
                             key=lambda x: x.start_time, reverse=True)[:10]
        
        for break_period in recent_breaks:
            start_time = self._format_timestamp(break_period.start_time)
            
            if break_period.end_time:
                end_time = self._format_timestamp(break_period.end_time)
                duration = self._format_seconds(self._break_duration_seconds(break_period))
                status = f"{start_time}-{end_time} ({duration})"
            else:
                status = f"{start_time}-ongoing"
            
            # Add text symbol based on break type
            symbol = {
                BreakType.LUNCH: "[L]",
                BreakType.COFFEE: "[C]",
                BreakType.GENERAL: "[B]"
            }.get(break_period.break_type, "[B]")
            
            break_text = f"{symbol} {break_period.break_type.value.title()}: {status}"
            self.breaks_listbox.insert(tk.END, break_text)
    
    def _break_duration_seconds(self, break_period: BreakPeriod) -> int:
        """Calculate break duration in seconds."""
        try:
            if break_period.start_time and break_period.end_time:
                start = self.time_calculator.parse_time(break_period.start_time)
                end = self.time_calculator.parse_time(break_period.end_time)
                return max(0, int((end - start).total_seconds()))
            if break_period.duration_minutes is not None:
                return max(0, int(break_period.duration_minutes * 60))
        except Exception as error:
            self.logger.debug(f"Failed to calculate break duration: {error}")
        return 0

    def _format_seconds(self, total_seconds: int) -> str:
        """Format seconds to HH:MM:SS string."""
        if total_seconds <= 0:
            return self.time_calculator.format_duration_with_seconds(0)
        return self.time_calculator.format_duration_with_seconds(total_seconds)

    def _format_timestamp(self, timestamp: str) -> str:
        """Format ISO timestamp to HH:MM:SS."""
        if not timestamp:
            return "--:--:--"
        try:
            dt_value = self.time_calculator.parse_time(timestamp)
            return dt_value.strftime("%H:%M:%S")
        except Exception:
            if 'T' in timestamp and len(timestamp.split('T')[1]) >= 8:
                return timestamp.split('T')[1][:8]
            return timestamp[:8] if len(timestamp) >= 8 else timestamp
    
    def get_break_summary(self) -> Dict[str, Any]:
        """Get summary of break data.
        
        Returns:
            Dictionary with break summary information
        """
        lunch_breaks = [b for b in self._break_periods if b.break_type == BreakType.LUNCH]
        coffee_breaks = [b for b in self._break_periods if b.break_type == BreakType.COFFEE]
        general_breaks = [b for b in self._break_periods if b.break_type == BreakType.GENERAL]
        
        return {
            'total_breaks': len(self._break_periods),
            'lunch': {
                'count': len(lunch_breaks),
                'time': sum(b.duration_minutes or 0 for b in lunch_breaks)
            },
            'coffee': {
                'count': len(coffee_breaks),
                'time': sum(b.duration_minutes or 0 for b in coffee_breaks)
            },
            'general': {
                'count': len(general_breaks),
                'time': sum(b.duration_minutes or 0 for b in general_breaks)
            },
            'total_time': sum(b.duration_minutes or 0 for b in self._break_periods)
        }