"""Coordinated export management for Worklog Manager."""

import os
import logging
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from data.database import Database
from core.data_aggregator import DataAggregator
from core.export_models import (
    ExportOptions,
    ExportFormat,
    ReportType,
    DateRange,
    ExportResult,
)
from exporters.csv_exporter import CSVExporter
from exporters.json_exporter import JSONExporter
from exporters.pdf_exporter import PDFExporter


class ExportManager:
    """High-level facade that orchestrates export operations."""

    def __init__(self, db: Database, export_dir: str = "exports"):
        self.db = db
        self.export_dir = export_dir
        self.logger = logging.getLogger(__name__)
        self.aggregator = DataAggregator(db)
        self.csv_exporter = CSVExporter(self.aggregator)
        self.json_exporter = JSONExporter(self.aggregator)
        self.pdf_exporter = PDFExporter(self.aggregator)

    def export_data(
        self,
        options: ExportOptions,
        output_path: Optional[str] = None,
    ) -> ExportResult:
        """Collect data and write it using the requested exporter."""
        valid, error = self.validate_date_range(
            options.date_range.start_date, options.date_range.end_date
        )
        if not valid:
            self.logger.error(f"Invalid export range: {error}")
            return ExportResult(success=False, error_message=error)

        try:
            export_data = self.aggregator.collect_export_data(options)
            filepath = self._resolve_target_path(options, output_path)
            exporter = self._resolve_exporter(options.format)
            result = exporter.export(export_data, filepath)
            if result.success:
                result.filepath = filepath
            return result
        except Exception as exc:
            self.logger.error(f"Export failed: {exc}")
            return ExportResult(success=False, error_message=str(exc))

    def export_today(
        self,
        export_format: ExportFormat = ExportFormat.CSV,
        report_type: ReportType = ReportType.DAILY_SUMMARY,
    ) -> ExportResult:
        today = date.today()
        options = ExportOptions(
            format=export_format,
            report_type=report_type,
            date_range=DateRange(today, today),
        )
        return self.export_data(options)

    def export_week(
        self,
        export_format: ExportFormat = ExportFormat.JSON,
        report_type: ReportType = ReportType.WEEKLY_SUMMARY,
    ) -> ExportResult:
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        options = ExportOptions(
            format=export_format,
            report_type=report_type,
            date_range=DateRange(start_date, end_date),
        )
        return self.export_data(options)

    def export_date_range(
        self,
        export_format: ExportFormat,
        start_date: date,
        end_date: date,
        report_type: ReportType,
        output_path: Optional[str] = None,
    ) -> ExportResult:
        options = ExportOptions(
            format=export_format,
            report_type=report_type,
            date_range=DateRange(start_date, end_date),
        )
        return self.export_data(options, output_path=output_path)

    def get_export_preview(self, options: ExportOptions) -> dict:
        """Return metadata about a potential export without writing files."""
        preview = {
            "date_range": {
                "start": options.date_range.start_date.isoformat(),
                "end": options.date_range.end_date.isoformat(),
            }
        }

        try:
            data = self.aggregator.collect_export_data(options)
            preview["data_counts"] = {
                "work_sessions": len(data.sessions),
                "breaks": len(data.breaks),
                "actions": len(data.actions),
                "work_days": len([d for d in data.daily_stats if d.total_work_minutes > 0]),
            }

            if data.daily_stats:
                trends = self.aggregator.get_productivity_trends(data.daily_stats)
                preview["statistics"] = {
                    "total_work_hours": round(trends["total_work_hours"], 2),
                    "average_work_hours": round(trends["average_work_hours"], 2),
                    "average_productivity": round(trends["average_productivity"], 1),
                }
        except Exception as exc:
            self.logger.error(f"Preview failed: {exc}")
            preview["error"] = str(exc)

        return preview

    def validate_date_range(self, start_date: date, end_date: date) -> Tuple[bool, Optional[str]]:
        """Ensure user-supplied dates are sensible."""
        if start_date > end_date:
            return False, "Start date cannot be after end date."

        today = date.today()
        if end_date > today:
            return False, "End date cannot be in the future."

        return True, None

    def _resolve_exporter(self, export_format: ExportFormat):
        if export_format == ExportFormat.CSV:
            return self.csv_exporter
        if export_format == ExportFormat.JSON:
            return self.json_exporter
        if export_format == ExportFormat.PDF:
            return self.pdf_exporter
        raise ValueError(f"Unsupported export format: {export_format}")

    def _generate_filepath(self, options: ExportOptions) -> str:
        os.makedirs(self.export_dir, exist_ok=True)
        start = options.date_range.start_date.isoformat()
        end = options.date_range.end_date.isoformat()
        timestamp = datetime.now().strftime("%H%M%S")
        if start == end:
            suffix = start
        else:
            suffix = f"{start}_to_{end}"
        filename = f"worklog_{options.report_type.value}_{suffix}_{timestamp}.{options.format.value}"
        return os.path.join(self.export_dir, filename)

    def _resolve_target_path(self, options: ExportOptions, output_path: Optional[str]) -> str:
        if output_path:
            return output_path

        if options.filename:
            if os.path.isabs(options.filename):
                return options.filename
            os.makedirs(self.export_dir, exist_ok=True)
            return os.path.join(self.export_dir, options.filename)

        return self._generate_filepath(options)