"""PDF export functionality for the Worklog Manager."""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image
    )
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from core.export_models import ExportData, ExportResult, ReportType
from core.data_aggregator import DataAggregator


class PDFExporter:
    """Handles PDF export functionality."""
    
    def __init__(self, aggregator: DataAggregator):
        """Initialize PDF exporter.
        
        Args:
            aggregator: Data aggregator instance
        """
        self.aggregator = aggregator
        self.logger = logging.getLogger(__name__)
        
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available. PDF export will be limited.")
    
    def export(self, export_data: ExportData, filepath: str) -> ExportResult:
        """Export data to PDF format.
        
        Args:
            export_data: Aggregated data to export
            filepath: Target file path
            
        Returns:
            Export result with success status
        """
        if not REPORTLAB_AVAILABLE:
            return self._export_simple_pdf(export_data, filepath)
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Generate content based on report type
            story = self._generate_pdf_content(export_data)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF export completed: {filepath}")
            
            return ExportResult(
                success=True,
                filepath=filepath,
                metadata={
                    'format': 'pdf',
                    'report_type': export_data.options.report_type.value,
                    'pages': 'generated'
                }
            )
            
        except Exception as e:
            self.logger.error(f"PDF export failed: {e}")
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    def _export_simple_pdf(self, export_data: ExportData, filepath: str) -> ExportResult:
        """Simple PDF export without ReportLab (plain text format)."""
        try:
            # Create simple text-based PDF content
            content = self._generate_simple_text_report(export_data)
            
            # Write lightweight PDF so readers can open the file without ReportLab
            self._write_basic_pdf(content, filepath)
            
            return ExportResult(
                success=True,
                filepath=filepath,
                metadata={'format': 'pdf_basic', 'warning': 'ReportLab not available - basic PDF generated'}
            )
            
        except Exception as e:
            return ExportResult(success=False, error_message=str(e))

    def _write_basic_pdf(self, text_content: str, filepath: str) -> None:
        """Write a minimal PDF document containing the provided text."""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)

        # Basic page/typography settings
        page_width = 595.0  # A4 width in PostScript points
        page_height = 842.0  # A4 height in PostScript points
        margin = 72.0  # 1 inch margin
        line_height = 14.0
        max_lines = max(1, int((page_height - 2 * margin) // line_height))

        # Prepare text lines, keep ASCII to simplify Type1 font usage
        lines = text_content.splitlines() or ["No report data available."]
        ascii_lines = [line.encode('ascii', 'replace').decode('ascii') for line in lines]

        # Break into pages respecting max_lines per page
        pages = [ascii_lines[i:i + max_lines] for i in range(0, len(ascii_lines), max_lines)] or [[]]

        objects: List[str] = ["", "", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
        page_numbers: List[int] = []

        for page_lines in pages:
            # Escape characters that have meaning in PDF text operators
            escaped_lines = [
                line.replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)') or ' '
                for line in page_lines
            ] or [' ']

            # Build text drawing commands
            text_commands = [
                'BT',
                '/F1 12 Tf',
                f'{line_height:.0f} TL',
                f'{margin:.0f} {page_height - margin:.0f} Td',
                f'({escaped_lines[0]}) Tj'
            ]

            for line in escaped_lines[1:]:
                text_commands.append('T*')
                text_commands.append(f'({line}) Tj')

            text_commands.append('ET')
            text_stream = "\n".join(text_commands) + "\n"
            stream_bytes = text_stream.encode('ascii')

            content_obj = (
                f"<< /Length {len(stream_bytes)} >>\n"
                "stream\n"
                f"{text_stream}"
                "endstream\n"
            )
            objects.append(content_obj)
            content_number = len(objects)

            page_obj = (
                "<< /Type /Page /Parent 2 0 R "
                f"/MediaBox [0 0 {page_width:.0f} {page_height:.0f}] "
                f"/Contents {content_number} 0 R "
                "/Resources << /Font << /F1 3 0 R >> >> >>"
            )
            objects.append(page_obj)
            page_numbers.append(len(objects))

        # Catalog and Pages objects now that page numbers are known
        kids_entries = " ".join(f"{num} 0 R" for num in page_numbers) or ""
        objects[0] = "<< /Type /Catalog /Pages 2 0 R >>"
        objects[1] = (
            "<< /Type /Pages "
            f"/Count {len(page_numbers)} "
            f"/Kids [{kids_entries}] >>"
        )

        # Assemble PDF with xref table
        pdf_bytes = bytearray(b"%PDF-1.4\n%\xC2\xB5\xC2\xB6\xC2\xB7\n")
        offsets = []

        for index, content in enumerate(objects, start=1):
            offsets.append(len(pdf_bytes))
            pdf_bytes.extend(f"{index} 0 obj\n".encode('ascii'))
            pdf_bytes.extend(content.encode('ascii'))
            pdf_bytes.extend(b"\nendobj\n")

        xref_offset = len(pdf_bytes)
        object_count = len(objects) + 1
        pdf_bytes.extend(f"xref\n0 {object_count}\n".encode('ascii'))
        pdf_bytes.extend(b"0000000000 65535 f \n")

        for offset in offsets:
            pdf_bytes.extend(f"{offset:010} 00000 n \n".encode('ascii'))

        pdf_bytes.extend(
            (
                "trailer\n"
                f"<< /Size {object_count} /Root 1 0 R >>\n"
                f"startxref\n{xref_offset}\n"
                "%%EOF\n"
            ).encode('ascii')
        )

        with open(filepath, 'wb') as pdf_file:
            pdf_file.write(pdf_bytes)
    
    def _generate_pdf_content(self, export_data: ExportData) -> List[Any]:
        """Generate PDF content elements.
        
        Args:
            export_data: Export data
            
        Returns:
            List of PDF elements
        """
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Title page
        story.append(Paragraph("Worklog Manager", title_style))
        story.append(Paragraph(f"{export_data.options.report_type.value.replace('_', ' ').title()} Report", subtitle_style))
        
        # Date range and metadata
        date_range = export_data.metadata['date_range']
        story.append(Paragraph(f"Report Period: {date_range['start']} to {date_range['end']}", styles['Normal']))
        story.append(Paragraph(f"Generated: {export_data.metadata['export_date'][:19]}", styles['Normal']))
        story.append(Paragraph(f"Total Days: {date_range['days_count']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Generate content based on report type
        report_type = export_data.options.report_type
        
        if report_type == ReportType.DAILY_SUMMARY:
            self._add_daily_summary_content(story, export_data, styles)
        elif report_type == ReportType.PRODUCTIVITY_REPORT:
            self._add_productivity_content(story, export_data, styles)
        elif report_type == ReportType.BREAK_ANALYSIS:
            self._add_break_analysis_content(story, export_data, styles)
        elif report_type == ReportType.WEEKLY_SUMMARY:
            self._add_weekly_summary_content(story, export_data, styles)
        else:
            self._add_detailed_content(story, export_data, styles)
        
        return story
    
    def _add_daily_summary_content(self, story: List[Any], export_data: ExportData, styles) -> None:
        """Add daily summary content to PDF.
        
        Args:
            story: PDF story elements
            export_data: Export data
            styles: ReportLab styles
        """
        story.append(Paragraph("Daily Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if not export_data.daily_stats:
            story.append(Paragraph("No data available for the selected date range.", styles['Normal']))
            return
        
        # Create daily summary table
        table_data = [
            ['Date', 'Work Hours', 'Break Hours', 'Productivity %', 'Overtime Hours']
        ]
        
        for day in export_data.daily_stats:
            if day.total_work_minutes > 0:  # Only show work days
                table_data.append([
                    day.date.strftime('%Y-%m-%d'),
                    f"{day.work_hours:.2f}",
                    f"{day.break_hours:.2f}",
                    f"{day.productivity_percentage:.1f}%",
                    f"{day.overtime_minutes / 60:.2f}"
                ])
        
        if len(table_data) > 1:  # Has data beyond header
            table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Add summary statistics
        self._add_summary_statistics(story, export_data, styles)
    
    def _add_productivity_content(self, story: List[Any], export_data: ExportData, styles) -> None:
        """Add productivity analysis content to PDF."""
        story.append(Paragraph("Productivity Analysis", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Get productivity trends
        trends = self.aggregator.get_productivity_trends(export_data.daily_stats)
        
        # Productivity metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Work Days', str(trends['work_days'])],
            ['Average Daily Work Hours', f"{trends['average_work_hours']:.2f}"],
            ['Average Daily Break Hours', f"{trends['average_break_hours']:.2f}"],
            ['Average Productivity', f"{trends['average_productivity']:.1f}%"],
            ['Total Work Hours', f"{trends['total_work_hours']:.2f}"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Daily productivity breakdown
        if export_data.daily_stats:
            story.append(Paragraph("Daily Productivity Breakdown", styles['Heading3']))
            story.append(Spacer(1, 12))
            
            productivity_data = [['Date', 'Work Hours', 'Productivity %', 'Status']]
            
            for day in export_data.daily_stats:
                status = 'Work Day' if day.total_work_minutes > 0 else 'No Work'
                productivity_data.append([
                    day.date.strftime('%Y-%m-%d'),
                    f"{day.work_hours:.2f}",
                    f"{day.productivity_percentage:.1f}%",
                    status
                ])
            
            prod_table = Table(productivity_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
            prod_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(prod_table)
    
    def _add_break_analysis_content(self, story: List[Any], export_data: ExportData, styles) -> None:
        """Add break analysis content to PDF."""
        story.append(Paragraph("Break Analysis", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if not export_data.breaks:
            story.append(Paragraph("No break data available for the selected period.", styles['Normal']))
            return
        
        # Get break analysis
        break_analysis = self.aggregator.get_break_analysis(export_data.breaks)
        
        # Break summary table
        summary_data = [
            ['Break Metric', 'Value'],
            ['Total Breaks', str(break_analysis['total_breaks'])],
            ['Total Break Time (minutes)', str(break_analysis['total_break_time'])],
            ['Average Break Duration (minutes)', f"{break_analysis['average_break_duration']:.1f}"],
            ['Longest Break (minutes)', str(break_analysis['longest_break'])],
            ['Shortest Break (minutes)', str(break_analysis['shortest_break'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Break type distribution
        story.append(Paragraph("Break Type Distribution", styles['Heading3']))
        story.append(Spacer(1, 12))
        
        dist_data = [['Break Type', 'Count', 'Percentage']]
        total_breaks = break_analysis['total_breaks']
        
        for break_type, count in break_analysis['break_type_distribution'].items():
            percentage = (count / total_breaks * 100) if total_breaks > 0 else 0
            dist_data.append([break_type, str(count), f"{percentage:.1f}%"])
        
        dist_table = Table(dist_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(dist_table)
    
    def _add_weekly_summary_content(self, story: List[Any], export_data: ExportData, styles) -> None:
        """Add weekly summary content to PDF."""
        story.append(Paragraph("Weekly Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if not export_data.weekly_stats:
            story.append(Paragraph("No weekly data available.", styles['Normal']))
            return
        
        # Weekly summary table
        weekly_data = [['Week Start', 'Week End', 'Total Work Hours', 'Avg Daily Work', 'Productivity %']]
        
        for week in export_data.weekly_stats:
            weekly_data.append([
                week.week_start.strftime('%Y-%m-%d'),
                week.week_end.strftime('%Y-%m-%d'),
                f"{week.total_work_minutes / 60:.2f}",
                f"{week.average_daily_work / 60:.2f}",
                f"{week.productivity_percentage:.1f}%"
            ])
        
        weekly_table = Table(weekly_data, colWidths=[1.2*inch, 1.2*inch, 1.3*inch, 1.3*inch, 1.2*inch])
        weekly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(weekly_table)
    
    def _add_detailed_content(self, story: List[Any], export_data: ExportData, styles) -> None:
        """Add detailed log content to PDF."""
        story.append(Paragraph("Detailed Work Log", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Work sessions
        if export_data.sessions:
            story.append(Paragraph("Work Sessions", styles['Heading3']))
            
            session_data = [['Date', 'Start Time', 'End Time', 'Work (min)', 'Breaks (min)']]
            
            for session in export_data.sessions:
                session_data.append([
                    session.date,
                    session.start_time[-8:] if session.start_time else '',  # Time only
                    session.end_time[-8:] if session.end_time else '',
                    str(session.total_work_minutes or 0),
                    str(session.total_break_minutes or 0)
                ])
            
            session_table = Table(session_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            session_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(session_table)
            story.append(Spacer(1, 20))
    
    def _add_summary_statistics(self, story: List[Any], export_data: ExportData, styles) -> None:
        """Add summary statistics section."""
        story.append(Paragraph("Summary Statistics", styles['Heading3']))
        story.append(Spacer(1, 12))
        
        trends = self.aggregator.get_productivity_trends(export_data.daily_stats)
        
        summary_text = f"""
        Total Work Days: {trends['work_days']}<br/>
        Average Daily Work Hours: {trends['average_work_hours']:.2f}<br/>
        Average Daily Break Hours: {trends['average_break_hours']:.2f}<br/>
        Average Productivity: {trends['average_productivity']:.1f}%<br/>
        Total Work Hours: {trends['total_work_hours']:.2f}
        """
        
        story.append(Paragraph(summary_text, styles['Normal']))
    
    def _generate_simple_text_report(self, export_data: ExportData) -> str:
        """Generate simple text report when ReportLab is not available."""
        content = []
        content.append("WORKLOG MANAGER REPORT")
        content.append("=" * 50)
        content.append(f"Generated: {export_data.metadata['export_date']}")
        content.append(f"Date Range: {export_data.metadata['date_range']['start']} to {export_data.metadata['date_range']['end']}")
        content.append("")
        
        # Daily summary
        if export_data.daily_stats:
            content.append("DAILY SUMMARY")
            content.append("-" * 30)
            content.append(f"{'Date':<12} {'Work Hrs':<10} {'Break Hrs':<10} {'Productivity':<12}")
            content.append("-" * 50)
            
            for day in export_data.daily_stats:
                if day.total_work_minutes > 0:
                    content.append(
                        f"{day.date.strftime('%Y-%m-%d'):<12} "
                        f"{day.work_hours:<10.2f} "
                        f"{day.break_hours:<10.2f} "
                        f"{day.productivity_percentage:<12.1f}%"
                    )
            content.append("")
        
        # Statistics
        if export_data.daily_stats:
            trends = self.aggregator.get_productivity_trends(export_data.daily_stats)
            content.append("STATISTICS")
            content.append("-" * 20)
            content.append(f"Total Work Days: {trends['work_days']}")
            content.append(f"Average Daily Work Hours: {trends['average_work_hours']:.2f}")
            content.append(f"Average Productivity: {trends['average_productivity']:.1f}%")
            content.append(f"Total Work Hours: {trends['total_work_hours']:.2f}")
        
        return "\n".join(content)