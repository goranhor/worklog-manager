"""JSON export functionality for the Worklog Manager."""

import json
import os
import logging
from datetime import datetime, date
from typing import Dict, Any
from dataclasses import asdict

from core.export_models import ExportData, ExportResult
from core.data_aggregator import DataAggregator


class JSONExporter:
    """Handles JSON export functionality."""
    
    def __init__(self, aggregator: DataAggregator):
        """Initialize JSON exporter.
        
        Args:
            aggregator: Data aggregator instance
        """
        self.aggregator = aggregator
        self.logger = logging.getLogger(__name__)
    
    def export(self, export_data: ExportData, filepath: str) -> ExportResult:
        """Export data to JSON format.
        
        Args:
            export_data: Aggregated data to export
            filepath: Target file path
            
        Returns:
            Export result with success status
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Convert data to JSON-serializable format
            json_data = self._prepare_json_data(export_data)
            
            # Write to file with proper formatting
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=2, ensure_ascii=False, default=self._json_serializer)
            
            self.logger.info(f"JSON export completed: {filepath}")
            
            return ExportResult(
                success=True,
                filepath=filepath,
                metadata={
                    'format': 'json',
                    'report_type': export_data.options.report_type.value,
                    'objects_exported': len(json_data)
                }
            )
            
        except Exception as e:
            self.logger.error(f"JSON export failed: {e}")
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    def _prepare_json_data(self, export_data: ExportData) -> Dict[str, Any]:
        """Prepare data for JSON serialization.
        
        Args:
            export_data: Export data
            
        Returns:
            JSON-serializable dictionary
        """
        # Base structure
        json_data = {
            'worklog_export': {
                'metadata': export_data.metadata.copy(),
                'export_options': {
                    'format': export_data.options.format.value,
                    'report_type': export_data.options.report_type.value,
                    'date_range': {
                        'start_date': export_data.options.date_range.start_date.isoformat(),
                        'end_date': export_data.options.date_range.end_date.isoformat(),
                        'days_count': export_data.options.date_range.days_count()
                    },
                    'include_breaks': export_data.options.include_breaks,
                    'include_actions': export_data.options.include_actions,
                    'include_analytics': export_data.options.include_analytics,
                    'group_by_date': export_data.options.group_by_date
                },
                'data': {}
            }
        }
        
        # Add work sessions
        if export_data.sessions:
            json_data['worklog_export']['data']['work_sessions'] = [
                self._serialize_session(session) for session in export_data.sessions
            ]
        
        # Add break periods
        if export_data.options.include_breaks and export_data.breaks:
            json_data['worklog_export']['data']['break_periods'] = [
                self._serialize_break(break_period) for break_period in export_data.breaks
            ]
        
        # Add action logs
        if export_data.options.include_actions and export_data.actions:
            json_data['worklog_export']['data']['action_logs'] = [
                self._serialize_action(action) for action in export_data.actions
            ]
        
        # Add analytics
        if export_data.options.include_analytics:
            analytics_data = {
                'daily_statistics': [
                    self._serialize_daily_stats(day) for day in export_data.daily_stats
                ],
                'weekly_statistics': [
                    self._serialize_weekly_stats(week) for week in export_data.weekly_stats
                ]
            }
            
            # Add productivity trends
            analytics_data['productivity_trends'] = self.aggregator.get_productivity_trends(
                export_data.daily_stats
            )
            
            # Add break analysis
            if export_data.breaks:
                analytics_data['break_analysis'] = self.aggregator.get_break_analysis(
                    export_data.breaks
                )
            
            json_data['worklog_export']['data']['analytics'] = analytics_data
        
        # Group data by date if requested
        if export_data.options.group_by_date:
            json_data['worklog_export']['data']['grouped_by_date'] = self._group_data_by_date(
                export_data
            )
        
        return json_data
    
    def _serialize_session(self, session) -> Dict[str, Any]:
        """Serialize a work session for JSON export.
        
        Args:
            session: Work session object
            
        Returns:
            Serializable dictionary
        """
        return {
            'id': session.id,
            'date': session.date,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'total_work_minutes': session.total_work_minutes,
            'total_break_minutes': session.total_break_minutes,
            'productive_minutes': session.productive_minutes,
            'overtime_minutes': session.overtime_minutes,
            'status': session.status.value if hasattr(session.status, 'value') else str(session.status),
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'updated_at': session.updated_at.isoformat() if session.updated_at else None
        }
    
    def _serialize_break(self, break_period) -> Dict[str, Any]:
        """Serialize a break period for JSON export.
        
        Args:
            break_period: Break period object
            
        Returns:
            Serializable dictionary
        """
        return {
            'id': break_period.id,
            'session_id': break_period.session_id,
            'break_type': break_period.break_type.value if hasattr(break_period.break_type, 'value') else str(break_period.break_type),
            'start_time': break_period.start_time,
            'end_time': break_period.end_time,
            'duration_minutes': break_period.duration_minutes,
            'created_at': break_period.created_at.isoformat() if break_period.created_at else None
        }
    
    def _serialize_action(self, action) -> Dict[str, Any]:
        """Serialize an action log for JSON export.
        
        Args:
            action: Action log object
            
        Returns:
            Serializable dictionary
        """
        return {
            'id': action.id,
            'session_id': action.session_id,
            'action_type': action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type),
            'timestamp': action.timestamp,
            'revoked': action.revoked,
            'created_at': action.created_at.isoformat() if action.created_at else None
        }
    
    def _serialize_daily_stats(self, day_stats) -> Dict[str, Any]:
        """Serialize daily statistics for JSON export.
        
        Args:
            day_stats: Daily statistics object
            
        Returns:
            Serializable dictionary
        """
        return {
            'date': day_stats.date.isoformat(),
            'total_work_minutes': day_stats.total_work_minutes,
            'total_break_minutes': day_stats.total_break_minutes,
            'productive_minutes': day_stats.productive_minutes,
            'overtime_minutes': day_stats.overtime_minutes,
            'breaks_count': day_stats.breaks_count,
            'coffee_breaks': day_stats.coffee_breaks,
            'lunch_breaks': day_stats.lunch_breaks,
            'general_breaks': day_stats.general_breaks,
            'sessions_count': day_stats.sessions_count,
            'first_start': day_stats.first_start.isoformat() if day_stats.first_start else None,
            'last_end': day_stats.last_end.isoformat() if day_stats.last_end else None,
            'work_hours': day_stats.work_hours,
            'break_hours': day_stats.break_hours,
            'productivity_percentage': day_stats.productivity_percentage
        }
    
    def _serialize_weekly_stats(self, week_stats) -> Dict[str, Any]:
        """Serialize weekly statistics for JSON export.
        
        Args:
            week_stats: Weekly statistics object
            
        Returns:
            Serializable dictionary
        """
        return {
            'week_start': week_stats.week_start.isoformat(),
            'week_end': week_stats.week_end.isoformat(),
            'total_work_minutes': week_stats.total_work_minutes,
            'total_break_minutes': week_stats.total_break_minutes,
            'average_daily_work': week_stats.average_daily_work,
            'productivity_percentage': week_stats.productivity_percentage,
            'daily_stats': [
                self._serialize_daily_stats(day) for day in week_stats.daily_stats
            ]
        }
    
    def _group_data_by_date(self, export_data: ExportData) -> Dict[str, Dict[str, Any]]:
        """Group all data by date for easier consumption.
        
        Args:
            export_data: Export data
            
        Returns:
            Data grouped by date
        """
        grouped_data = {}
        
        # Create date entries
        for day_stats in export_data.daily_stats:
            date_key = day_stats.date.isoformat()
            grouped_data[date_key] = {
                'date': date_key,
                'daily_stats': self._serialize_daily_stats(day_stats),
                'work_sessions': [],
                'break_periods': [],
                'action_logs': []
            }
        
        # Add sessions to their dates
        for session in export_data.sessions:
            session_date = session.date
            if session_date in grouped_data:
                grouped_data[session_date]['work_sessions'].append(
                    self._serialize_session(session)
                )
        
        # Add breaks to their dates
        for break_period in export_data.breaks:
            # Find the session date for this break
            session_date = None
            for session in export_data.sessions:
                if session.id == break_period.session_id:
                    session_date = session.date
                    break
            
            if session_date and session_date in grouped_data:
                grouped_data[session_date]['break_periods'].append(
                    self._serialize_break(break_period)
                )
        
        # Add actions to their dates
        for action in export_data.actions:
            # Find the session date for this action
            session_date = None
            for session in export_data.sessions:
                if session.id == action.session_id:
                    session_date = session.date
                    break
            
            if session_date and session_date in grouped_data:
                grouped_data[session_date]['action_logs'].append(
                    self._serialize_action(action)
                )
        
        return grouped_data
    
    def _json_serializer(self, obj) -> str:
        """Custom JSON serializer for datetime objects and other types.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serialized string
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif hasattr(obj, 'value'):  # Enum objects
            return obj.value
        elif hasattr(obj, '__dict__'):  # Other objects
            return obj.__dict__
        
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def create_compact_export(self, export_data: ExportData, filepath: str) -> ExportResult:
        """Create a compact JSON export with minimal data.
        
        Args:
            export_data: Aggregated data to export
            filepath: Target file path
            
        Returns:
            Export result with success status
        """
        try:
            # Create compact structure
            compact_data = {
                'export_date': export_data.metadata['export_date'],
                'date_range': export_data.metadata['date_range'],
                'summary': {}
            }
            
            # Add only essential data
            if export_data.daily_stats:
                compact_data['daily_summary'] = [
                    {
                        'date': day.date.isoformat(),
                        'work_hours': round(day.work_hours, 2),
                        'break_hours': round(day.break_hours, 2),
                        'productivity': round(day.productivity_percentage, 1)
                    }
                    for day in export_data.daily_stats
                    if day.total_work_minutes > 0  # Only include work days
                ]
            
            # Add summary statistics
            if export_data.daily_stats:
                trends = self.aggregator.get_productivity_trends(export_data.daily_stats)
                compact_data['summary'] = {
                    'total_work_hours': round(trends['total_work_hours'], 2),
                    'work_days': trends['work_days'],
                    'avg_daily_hours': round(trends['average_work_hours'], 2),
                    'avg_productivity': round(trends['average_productivity'], 1)
                }
            
            # Write compact file
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(compact_data, file, indent=2, ensure_ascii=False)
            
            return ExportResult(
                success=True,
                filepath=filepath,
                metadata={'format': 'json_compact', 'size': 'minimal'}
            )
            
        except Exception as e:
            self.logger.error(f"Compact JSON export failed: {e}")
            return ExportResult(success=False, error_message=str(e))