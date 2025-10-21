"""Data aggregation and statistics calculation for export functionality."""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict

from data.database import Database
from data.models import WorkSession, BreakPeriod, ActionLog, BreakType
from core.export_models import DailyStats, WeeklyStats, ExportData, ExportOptions, DateRange


class DataAggregator:
    """Aggregates and calculates statistics for export data."""
    
    def __init__(self, db: Database):
        """Initialize the data aggregator.
        
        Args:
            db: Database instance
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def collect_export_data(self, options: ExportOptions) -> ExportData:
        """Collect all data needed for export.
        
        Args:
            options: Export configuration options
            
        Returns:
            Aggregated export data
        """
        try:
            export_data = ExportData(options=options)
            
            # Collect raw data within date range
            export_data.sessions = self._get_sessions_in_range(options.date_range)
            
            if options.include_breaks:
                export_data.breaks = self._get_breaks_in_range(options.date_range)
            
            if options.include_actions:
                export_data.actions = self._get_actions_in_range(options.date_range)
            
            # Calculate statistics
            if options.include_analytics:
                export_data.daily_stats = self._calculate_daily_stats(
                    export_data.sessions, export_data.breaks, options.date_range
                )
                export_data.weekly_stats = self._calculate_weekly_stats(export_data.daily_stats)
            
            self.logger.info(f"Collected export data for {options.date_range.days_count()} days")
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect export data: {e}")
            raise
    
    def _get_sessions_in_range(self, date_range: DateRange) -> List[WorkSession]:
        """Get work sessions within date range.
        
        Args:
            date_range: Date range to filter by
            
        Returns:
            List of work sessions
        """
        sessions = []
        current_date = date_range.start_date
        
        while current_date <= date_range.end_date:
            session = self.db.get_session_by_date(current_date.isoformat())
            if session:
                sessions.append(session)
            current_date += timedelta(days=1)
        
        return sessions
    
    def _get_breaks_in_range(self, date_range: DateRange) -> List[BreakPeriod]:
        """Get break periods within date range.
        
        Args:
            date_range: Date range to filter by
            
        Returns:
            List of break periods
        """
        breaks = []
        sessions = self._get_sessions_in_range(date_range)
        
        for session in sessions:
            session_breaks = self.db.get_session_breaks(session.id)
            breaks.extend(session_breaks)
        
        return breaks
    
    def _get_actions_in_range(self, date_range: DateRange) -> List[ActionLog]:
        """Get action logs within date range.
        
        Args:
            date_range: Date range to filter by
            
        Returns:
            List of action logs
        """
        actions = []
        sessions = self._get_sessions_in_range(date_range)
        
        for session in sessions:
            session_actions = self.db.get_session_actions(session.id)
            actions.extend(session_actions)
        
        return actions
    
    def _calculate_daily_stats(self, sessions: List[WorkSession], 
                             breaks: List[BreakPeriod], date_range: DateRange) -> List[DailyStats]:
        """Calculate daily statistics.
        
        Args:
            sessions: Work sessions
            breaks: Break periods
            date_range: Date range for calculations
            
        Returns:
            List of daily statistics
        """
        daily_stats = []
        
        # Group sessions by date
        sessions_by_date = defaultdict(list)
        for session in sessions:
            session_date = datetime.fromisoformat(session.date).date()
            sessions_by_date[session_date].append(session)
        
        # Group breaks by session
        breaks_by_session = defaultdict(list)
        for break_period in breaks:
            breaks_by_session[break_period.session_id].extend([break_period])
        
        # Calculate stats for each day in range
        current_date = date_range.start_date
        while current_date <= date_range.end_date:
            day_sessions = sessions_by_date.get(current_date, [])
            
            if day_sessions:
                # Calculate from actual session data
                main_session = day_sessions[0]  # Should be only one session per day
                session_breaks = breaks_by_session.get(main_session.id, [])
                
                stats = DailyStats(
                    date=current_date,
                    total_work_minutes=main_session.total_work_minutes or 0,
                    total_break_minutes=main_session.total_break_minutes or 0,
                    productive_minutes=main_session.productive_minutes or 0,
                    overtime_minutes=main_session.overtime_minutes or 0,
                    breaks_count=len(session_breaks),
                    coffee_breaks=len([b for b in session_breaks if b.break_type == BreakType.COFFEE]),
                    lunch_breaks=len([b for b in session_breaks if b.break_type == BreakType.LUNCH]),
                    general_breaks=len([b for b in session_breaks if b.break_type == BreakType.GENERAL]),
                    sessions_count=len(day_sessions),
                    first_start=datetime.fromisoformat(main_session.start_time) if main_session.start_time else None,
                    last_end=datetime.fromisoformat(main_session.end_time) if main_session.end_time else None
                )
            else:
                # No session for this day - create empty stats
                stats = DailyStats(
                    date=current_date,
                    total_work_minutes=0,
                    total_break_minutes=0,
                    productive_minutes=0,
                    overtime_minutes=0,
                    breaks_count=0,
                    coffee_breaks=0,
                    lunch_breaks=0,
                    general_breaks=0,
                    sessions_count=0
                )
            
            daily_stats.append(stats)
            current_date += timedelta(days=1)
        
        return daily_stats
    
    def _calculate_weekly_stats(self, daily_stats: List[DailyStats]) -> List[WeeklyStats]:
        """Calculate weekly statistics from daily stats.
        
        Args:
            daily_stats: List of daily statistics
            
        Returns:
            List of weekly statistics
        """
        if not daily_stats:
            return []
        
        weekly_stats = []
        
        # Group daily stats by week
        weeks = defaultdict(list)
        for day_stats in daily_stats:
            # Get Monday of the week (ISO week start)
            week_start = day_stats.date - timedelta(days=day_stats.date.weekday())
            weeks[week_start].append(day_stats)
        
        # Create weekly stats for each week
        for week_start, week_days in weeks.items():
            week_end = week_start + timedelta(days=6)
            
            week_stats = WeeklyStats(
                week_start=week_start,
                week_end=week_end,
                daily_stats=sorted(week_days, key=lambda x: x.date)
            )
            weekly_stats.append(week_stats)
        
        return sorted(weekly_stats, key=lambda x: x.week_start)
    
    def get_productivity_trends(self, daily_stats: List[DailyStats]) -> Dict[str, float]:
        """Calculate productivity trends.
        
        Args:
            daily_stats: List of daily statistics
            
        Returns:
            Dictionary with trend metrics
        """
        work_days = [day for day in daily_stats if day.total_work_minutes > 0]
        
        if not work_days:
            return {
                'average_work_hours': 0.0,
                'average_break_hours': 0.0,
                'average_productivity': 0.0,
                'total_work_hours': 0.0,
                'total_days': len(daily_stats),
                'work_days': 0
            }
        
        total_work_minutes = sum(day.total_work_minutes for day in work_days)
        total_break_minutes = sum(day.total_break_minutes for day in work_days)
        
        return {
            'average_work_hours': (total_work_minutes / len(work_days)) / 60.0,
            'average_break_hours': (total_break_minutes / len(work_days)) / 60.0,
            'average_productivity': sum(day.productivity_percentage for day in work_days) / len(work_days),
            'total_work_hours': total_work_minutes / 60.0,
            'total_days': len(daily_stats),
            'work_days': len(work_days)
        }
    
    def get_break_analysis(self, breaks: List[BreakPeriod]) -> Dict[str, Any]:
        """Analyze break patterns.
        
        Args:
            breaks: List of break periods
            
        Returns:
            Dictionary with break analysis
        """
        if not breaks:
            return {
                'total_breaks': 0,
                'total_break_time': 0,
                'average_break_duration': 0,
                'break_type_distribution': {},
                'longest_break': 0,
                'shortest_break': 0
            }
        
        # Calculate break statistics
        durations = [b.duration_minutes for b in breaks if b.duration_minutes]
        break_types = [b.break_type for b in breaks]
        
        type_counts = {}
        for break_type in BreakType:
            type_counts[break_type.value] = break_types.count(break_type)
        
        return {
            'total_breaks': len(breaks),
            'total_break_time': sum(durations),
            'average_break_duration': sum(durations) / len(durations) if durations else 0,
            'break_type_distribution': type_counts,
            'longest_break': max(durations) if durations else 0,
            'shortest_break': min(durations) if durations else 0
        }