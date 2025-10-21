"""Main export manager coordinating all export functionality."""

import os
import logging
from datetime import date, datetime
from typing import Optional

from data.database import Database
from core.export_models import ExportOptions, ExportFormat, ExportResult, DateRange
from core.data_aggregator import DataAggregator
from exporters.csv_exporter import CSVExporter
from exporters.json_exporter import JSONExporter
from exporters.pdf_exporter import PDFExporter


class ExportManager:
    """Main export manager coordinating all export functionality."""
    
    def __init__(self, db: Database):
        """Initialize export manager.
        
        Args:
            db: Database instance
        """
        self.db = db
        self.aggregator = DataAggregator(db)
        self.csv_exporter = CSVExporter(self.aggregator)
        self.json_exporter = JSONExporter(self.aggregator)
        self.pdf_exporter = PDFExporter(self.aggregator)
        self.logger = logging.getLogger(__name__)
        
        # Default export directory
        self.default_export_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(self.default_export_dir, exist_ok=True)
    
    def export_data(self, options: ExportOptions, 
                   custom_filepath: Optional[str] = None) -> ExportResult:
        """Export data according to the specified options.
        
        Args:
            options: Export configuration
            custom_filepath: Custom file path (optional)
            
        Returns:
            Export result with success status
        """
        try:
            # Generate filename if not provided
            if custom_filepath:
                filepath = custom_filepath
            else:
                filepath = self._generate_filepath(options)
            
            # Collect export data
            self.logger.info(f"Collecting export data for {options.format.value} export")
            export_data = self.aggregator.collect_export_data(options)
            
            # Export based on format
            if options.format == ExportFormat.CSV:
                result = self.csv_exporter.export(export_data, filepath)
            elif options.format == ExportFormat.JSON:
                result = self.json_exporter.export(export_data, filepath)
            elif options.format == ExportFormat.PDF:
                result = self.pdf_exporter.export(export_data, filepath)
            else:
                raise ValueError(f"Unsupported export format: {options.format}")
            
            if result.success:
                self.logger.info(f"Export completed successfully: {result.filepath}")
            else:
                self.logger.error(f"Export failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Export operation failed: {e}")
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    def export_today(self, format: ExportFormat) -> ExportResult:
        """Export today's data in the specified format.
        
        Args:
            format: Export format
            
        Returns:
            Export result
        """
        from core.export_models import ReportType
        
        today = date.today()
        options = ExportOptions(
            format=format,
            report_type=ReportType.DAILY_SUMMARY,
            date_range=DateRange(today, today)
        )
        
        return self.export_data(options)
    
    def export_week(self, format: ExportFormat, week_start: Optional[date] = None) -> ExportResult:
        """Export current or specified week's data.
        
        Args:
            format: Export format
            week_start: Start of week (defaults to current week)
            
        Returns:
            Export result
        """
        from datetime import timedelta
        from core.export_models import ReportType
        
        if week_start is None:
            today = date.today()
            # Get Monday of current week
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        options = ExportOptions(
            format=format,
            report_type=ReportType.WEEKLY_SUMMARY,
            date_range=DateRange(week_start, week_end)
        )
        
        return self.export_data(options)
    
    def export_month(self, format: ExportFormat, year: Optional[int] = None, 
                    month: Optional[int] = None) -> ExportResult:
        """Export current or specified month's data.
        
        Args:
            format: Export format
            year: Year (defaults to current)
            month: Month (defaults to current)
            
        Returns:
            Export result
        """
        from calendar import monthrange
        from core.export_models import ReportType
        
        if year is None or month is None:
            today = date.today()
            year = year or today.year
            month = month or today.month
        
        month_start = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        month_end = date(year, month, last_day)
        
        options = ExportOptions(
            format=format,
            report_type=ReportType.MONTHLY_SUMMARY,
            date_range=DateRange(month_start, month_end)
        )
        
        return self.export_data(options)
    
    def export_date_range(self, format: ExportFormat, start_date: date, 
                         end_date: date, report_type=None) -> ExportResult:
        """Export data for a custom date range.
        
        Args:
            format: Export format
            start_date: Start date
            end_date: End date
            report_type: Type of report (defaults to detailed log)
            
        Returns:
            Export result
        """
        from core.export_models import ReportType
        
        if report_type is None:
            report_type = ReportType.DETAILED_LOG
        
        options = ExportOptions(
            format=format,
            report_type=report_type,
            date_range=DateRange(start_date, end_date)
        )
        
        return self.export_data(options)
    
    def get_export_preview(self, options: ExportOptions) -> dict:
        """Get a preview of what will be exported.
        
        Args:
            options: Export options
            
        Returns:
            Preview data dictionary
        """
        try:
            export_data = self.aggregator.collect_export_data(options)
            
            preview = {
                'date_range': {
                    'start': options.date_range.start_date.isoformat(),
                    'end': options.date_range.end_date.isoformat(),
                    'days': options.date_range.days_count()
                },
                'data_counts': {
                    'work_sessions': len(export_data.sessions),
                    'break_periods': len(export_data.breaks),
                    'action_logs': len(export_data.actions),
                    'work_days': len([d for d in export_data.daily_stats if d.total_work_minutes > 0])
                },
                'format': options.format.value,
                'report_type': options.report_type.value
            }
            
            # Add summary statistics if available
            if export_data.daily_stats:
                trends = self.aggregator.get_productivity_trends(export_data.daily_stats)
                preview['statistics'] = {
                    'total_work_hours': round(trends['total_work_hours'], 2),
                    'average_daily_hours': round(trends['average_work_hours'], 2),
                    'work_days': trends['work_days'],
                    'avg_productivity': round(trends['average_productivity'], 1)
                }
            
            return preview
            
        except Exception as e:
            self.logger.error(f"Failed to generate export preview: {e}")
            return {'error': str(e)}
    
    def _generate_filepath(self, options: ExportOptions) -> str:
        """Generate automatic filepath for export.
        
        Args:
            options: Export options
            
        Returns:
            Generated filepath
        """
        # Create date-based filename
        start_date = options.date_range.start_date
        end_date = options.date_range.end_date
        
        if start_date == end_date:
            date_part = start_date.strftime('%Y-%m-%d')
        else:
            date_part = f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}"
        
        # Create filename
        report_type = options.report_type.value
        timestamp = datetime.now().strftime('%H%M%S')
        
        filename = f"worklog_{report_type}_{date_part}_{timestamp}.{options.format.value}"
        
        return os.path.join(self.default_export_dir, filename)
    
    def set_export_directory(self, directory: str) -> bool:
        """Set the default export directory.
        
        Args:
            directory: Directory path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(directory, exist_ok=True)
            self.default_export_dir = directory
            self.logger.info(f"Export directory set to: {directory}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set export directory: {e}")
            return False
    
    def get_available_formats(self) -> list:
        """Get list of available export formats.
        
        Returns:
            List of format names
        """
        return [format.value for format in ExportFormat]
    
    def get_available_report_types(self) -> list:
        """Get list of available report types.
        
        Returns:
            List of report type names
        """
        from core.export_models import ReportType
        return [report.value for report in ReportType]
    
    def validate_date_range(self, start_date: date, end_date: date) -> tuple:
        """Validate a date range for export.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if start_date > end_date:
                return False, "Start date cannot be after end date"
            
            if start_date > date.today():
                return False, "Start date cannot be in the future"
            
            # Check if date range is too large (more than 1 year)
            days_diff = (end_date - start_date).days
            if days_diff > 365:
                return False, "Date range cannot exceed 1 year"
            
            # Check if there's any data in the range
            date_range = DateRange(start_date, end_date)
            sessions = self.aggregator._get_sessions_in_range(date_range)
            
            if not sessions:
                return False, "No work data found in the specified date range"
            
            return True, ""
            
        except Exception as e:
            return False, f"Date validation error: {str(e)}"