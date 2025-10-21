"""CSV export functionality for the Worklog Manager."""

import csv
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from io import StringIO

from core.export_models import ExportData, ExportResult, ReportType
from core.data_aggregator import DataAggregator


class CSVExporter:
    """Handles CSV export functionality."""
    
    def __init__(self, aggregator: DataAggregator):
        """Initialize CSV exporter.
        
        Args:
            aggregator: Data aggregator instance
        """
        self.aggregator = aggregator
        self.logger = logging.getLogger(__name__)
    
    def export(self, export_data: ExportData, filepath: str) -> ExportResult:
        """Export data to CSV format.
        
        Args:
            export_data: Aggregated data to export
            filepath: Target file path
            
        Returns:
            Export result with success status
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Generate CSV content based on report type
            csv_content = self._generate_csv_content(export_data)
            
            # Write to file
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                file.write(csv_content)
            
            self.logger.info(f"CSV export completed: {filepath}")
            
            return ExportResult(
                success=True,
                filepath=filepath,
                metadata={
                    'format': 'csv',
                    'report_type': export_data.options.report_type.value,
                    'rows_exported': csv_content.count('\n')
                }
            )
            
        except Exception as e:
            self.logger.error(f"CSV export failed: {e}")
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    def _generate_csv_content(self, export_data: ExportData) -> str:
        """Generate CSV content based on report type.
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content as string
        """
        report_type = export_data.options.report_type
        
        if report_type == ReportType.DAILY_SUMMARY:
            return self._generate_daily_summary_csv(export_data)
        elif report_type == ReportType.DETAILED_LOG:
            return self._generate_detailed_log_csv(export_data)
        elif report_type == ReportType.BREAK_ANALYSIS:
            return self._generate_break_analysis_csv(export_data)
        elif report_type == ReportType.PRODUCTIVITY_REPORT:
            return self._generate_productivity_csv(export_data)
        elif report_type == ReportType.WEEKLY_SUMMARY:
            return self._generate_weekly_summary_csv(export_data)
        elif report_type == ReportType.MONTHLY_SUMMARY:
            return self._generate_monthly_summary_csv(export_data)
        else:
            return self._generate_default_csv(export_data)
    
    def _generate_daily_summary_csv(self, export_data: ExportData) -> str:
        """Generate daily summary CSV.
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header with metadata
        writer.writerow(['Worklog Manager - Daily Summary Report'])
        writer.writerow(['Generated:', export_data.metadata['export_date']])
        writer.writerow(['Date Range:', f"{export_data.metadata['date_range']['start']} to {export_data.metadata['date_range']['end']}"])
        writer.writerow([])  # Empty row
        
        # Daily summary headers
        headers = [
            'Date', 'Work Hours', 'Break Hours', 'Productive Hours',
            'Overtime Hours', 'Total Breaks', 'Coffee Breaks', 'Lunch Breaks',
            'General Breaks', 'Productivity %', 'First Start', 'Last End'
        ]
        writer.writerow(headers)
        
        # Daily summary data
        for day in export_data.daily_stats:
            row = [
                day.date.strftime('%Y-%m-%d'),
                f"{day.work_hours:.2f}",
                f"{day.break_hours:.2f}",
                f"{day.productive_minutes / 60:.2f}",
                f"{day.overtime_minutes / 60:.2f}",
                day.breaks_count,
                day.coffee_breaks,
                day.lunch_breaks,
                day.general_breaks,
                f"{day.productivity_percentage:.1f}%",
                day.first_start.strftime('%H:%M:%S') if day.first_start else '',
                day.last_end.strftime('%H:%M:%S') if day.last_end else ''
            ]
            writer.writerow(row)
        
        # Summary statistics
        if export_data.daily_stats:
            writer.writerow([])  # Empty row
            writer.writerow(['Summary Statistics'])
            
            trends = self.aggregator.get_productivity_trends(export_data.daily_stats)
            
            writer.writerow(['Total Work Days:', trends['work_days']])
            writer.writerow(['Average Work Hours:', f"{trends['average_work_hours']:.2f}"])
            writer.writerow(['Average Break Hours:', f"{trends['average_break_hours']:.2f}"])
            writer.writerow(['Average Productivity:', f"{trends['average_productivity']:.1f}%"])
            writer.writerow(['Total Work Hours:', f"{trends['total_work_hours']:.2f}"])
        
        return output.getvalue()
    
    def _generate_detailed_log_csv(self, export_data: ExportData) -> str:
        """Generate detailed log CSV with all actions and sessions.
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Worklog Manager - Detailed Log Report'])
        writer.writerow(['Generated:', export_data.metadata['export_date']])
        writer.writerow([])
        
        # Work sessions section
        if export_data.sessions:
            writer.writerow(['Work Sessions'])
            headers = ['Date', 'Start Time', 'End Time', 'Total Work (min)', 
                      'Total Breaks (min)', 'Productive (min)', 'Overtime (min)', 'Status']
            writer.writerow(headers)
            
            for session in export_data.sessions:
                row = [
                    session.date,
                    session.start_time or '',
                    session.end_time or '',
                    session.total_work_minutes or 0,
                    session.total_break_minutes or 0,
                    session.productive_minutes or 0,
                    session.overtime_minutes or 0,
                    session.status.value if hasattr(session.status, 'value') else str(session.status)
                ]
                writer.writerow(row)
            writer.writerow([])
        
        # Break periods section
        if export_data.breaks:
            writer.writerow(['Break Periods'])
            headers = ['Date', 'Break Type', 'Start Time', 'End Time', 'Duration (min)']
            writer.writerow(headers)
            
            for break_period in export_data.breaks:
                # Get session date for this break
                session_date = ''
                for session in export_data.sessions:
                    if session.id == break_period.session_id:
                        session_date = session.date
                        break
                
                row = [
                    session_date,
                    break_period.break_type.value if hasattr(break_period.break_type, 'value') else str(break_period.break_type),
                    break_period.start_time or '',
                    break_period.end_time or '',
                    break_period.duration_minutes or 0
                ]
                writer.writerow(row)
            writer.writerow([])
        
        # Actions section
        if export_data.actions:
            writer.writerow(['Action Log'])
            headers = ['Date', 'Time', 'Action Type', 'Revoked']
            writer.writerow(headers)
            
            for action in export_data.actions:
                # Get session date for this action
                session_date = ''
                for session in export_data.sessions:
                    if session.id == action.session_id:
                        session_date = session.date
                        break
                
                timestamp = datetime.fromisoformat(action.timestamp)
                row = [
                    session_date,
                    timestamp.strftime('%H:%M:%S'),
                    action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type),
                    'Yes' if action.revoked else 'No'
                ]
                writer.writerow(row)
        
        return output.getvalue()
    
    def _generate_break_analysis_csv(self, export_data: ExportData) -> str:
        """Generate break analysis CSV.
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Worklog Manager - Break Analysis Report'])
        writer.writerow(['Generated:', export_data.metadata['export_date']])
        writer.writerow([])
        
        # Break analysis
        break_analysis = self.aggregator.get_break_analysis(export_data.breaks)
        
        writer.writerow(['Break Summary'])
        writer.writerow(['Total Breaks:', break_analysis['total_breaks']])
        writer.writerow(['Total Break Time (minutes):', break_analysis['total_break_time']])
        writer.writerow(['Average Break Duration (minutes):', f"{break_analysis['average_break_duration']:.1f}"])
        writer.writerow(['Longest Break (minutes):', break_analysis['longest_break']])
        writer.writerow(['Shortest Break (minutes):', break_analysis['shortest_break']])
        writer.writerow([])
        
        # Break type distribution
        writer.writerow(['Break Type Distribution'])
        writer.writerow(['Break Type', 'Count', 'Percentage'])
        
        total_breaks = break_analysis['total_breaks']
        for break_type, count in break_analysis['break_type_distribution'].items():
            percentage = (count / total_breaks * 100) if total_breaks > 0 else 0
            writer.writerow([break_type, count, f"{percentage:.1f}%"])
        
        writer.writerow([])
        
        # Individual breaks
        if export_data.breaks:
            writer.writerow(['Individual Breaks'])
            writer.writerow(['Date', 'Break Type', 'Start Time', 'Duration (min)'])
            
            for break_period in export_data.breaks:
                # Get session date
                session_date = ''
                for session in export_data.sessions:
                    if session.id == break_period.session_id:
                        session_date = session.date
                        break
                
                start_time = ''
                if break_period.start_time:
                    start_time = datetime.fromisoformat(break_period.start_time).strftime('%H:%M:%S')
                
                row = [
                    session_date,
                    break_period.break_type.value if hasattr(break_period.break_type, 'value') else str(break_period.break_type),
                    start_time,
                    break_period.duration_minutes or 0
                ]
                writer.writerow(row)
        
        return output.getvalue()
    
    def _generate_productivity_csv(self, export_data: ExportData) -> str:
        """Generate productivity report CSV.
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Worklog Manager - Productivity Report'])
        writer.writerow(['Generated:', export_data.metadata['export_date']])
        writer.writerow([])
        
        # Productivity trends
        trends = self.aggregator.get_productivity_trends(export_data.daily_stats)
        
        writer.writerow(['Productivity Metrics'])
        writer.writerow(['Total Days Analyzed:', trends['total_days']])
        writer.writerow(['Active Work Days:', trends['work_days']])
        writer.writerow(['Average Daily Work Hours:', f"{trends['average_work_hours']:.2f}"])
        writer.writerow(['Average Daily Break Hours:', f"{trends['average_break_hours']:.2f}"])
        writer.writerow(['Average Productivity Percentage:', f"{trends['average_productivity']:.1f}%"])
        writer.writerow(['Total Work Hours:', f"{trends['total_work_hours']:.2f}"])
        writer.writerow([])
        
        # Daily productivity breakdown
        writer.writerow(['Daily Productivity Breakdown'])
        writer.writerow(['Date', 'Work Hours', 'Productivity %', 'Status'])
        
        for day in export_data.daily_stats:
            status = 'Work Day' if day.total_work_minutes > 0 else 'No Work'
            row = [
                day.date.strftime('%Y-%m-%d'),
                f"{day.work_hours:.2f}",
                f"{day.productivity_percentage:.1f}%",
                status
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    def _generate_weekly_summary_csv(self, export_data: ExportData) -> str:
        """Generate weekly summary CSV.
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Worklog Manager - Weekly Summary Report'])
        writer.writerow(['Generated:', export_data.metadata['export_date']])
        writer.writerow([])
        
        # Weekly summary headers
        headers = ['Week Start', 'Week End', 'Total Work Hours', 
                  'Total Break Hours', 'Average Daily Work', 'Productivity %', 'Work Days']
        writer.writerow(headers)
        
        # Weekly data
        for week in export_data.weekly_stats:
            work_days = len([day for day in week.daily_stats if day.total_work_minutes > 0])
            row = [
                week.week_start.strftime('%Y-%m-%d'),
                week.week_end.strftime('%Y-%m-%d'),
                f"{week.total_work_minutes / 60:.2f}",
                f"{week.total_break_minutes / 60:.2f}",
                f"{week.average_daily_work / 60:.2f}",
                f"{week.productivity_percentage:.1f}%",
                work_days
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    def _generate_monthly_summary_csv(self, export_data: ExportData) -> str:
        """Generate monthly summary CSV (similar to weekly but grouped by month).
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content string
        """
        # For now, use daily summary format
        # This could be enhanced to group by month
        return self._generate_daily_summary_csv(export_data)
    
    def _generate_default_csv(self, export_data: ExportData) -> str:
        """Generate default CSV format (daily summary).
        
        Args:
            export_data: Export data
            
        Returns:
            CSV content string
        """
        return self._generate_daily_summary_csv(export_data)