#!/usr/bin/env python3
"""Test script for Phase 3 Export functionality."""

import sys
import os
import logging
from datetime import datetime, date, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.worklog_manager import WorklogManager
from core.export_manager import ExportManager
from core.export_models import ExportOptions, ExportFormat, ReportType, DateRange
from data.models import WorklogState, BreakType

def test_export_functionality():
    """Test the export functionality."""
    print("Testing Export Functionality - Phase 3")
    print("=" * 60)
    
    # Create worklog manager with test database
    test_db_path = "test_export.db"
    
    # Clean up any existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Clean up existing exports
    export_dir = "exports"
    if os.path.exists(export_dir):
        for file in os.listdir(export_dir):
            if file.startswith("worklog_"):
                os.remove(os.path.join(export_dir, file))
    
    try:
        # Create test data
        print("1. Setting up test data...")
        manager = WorklogManager(test_db_path)
        export_manager = ExportManager(manager.db)
        
        # Create a few days of test data
        test_dates = [
            date.today() - timedelta(days=2),
            date.today() - timedelta(days=1),
            date.today()
        ]
        
        for i, test_date in enumerate(test_dates):
            print(f"   Creating data for {test_date}")
            
            # Start day
            manager.start_day()
            
            # Add some breaks
            manager.stop_work(BreakType.COFFEE)
            manager.continue_work()
            
            if i == 1:  # Add lunch break on second day
                manager.stop_work(BreakType.LUNCH)
                manager.continue_work()
            
            # End day
            manager.end_day()
            
            # Manually update session date for testing
            session = manager.current_session
            if session:
                with manager.db.get_connection() as conn:
                    conn.execute(
                        "UPDATE work_sessions SET date = ?, total_work_minutes = ?, productive_minutes = ? WHERE id = ?",
                        (test_date.isoformat(), 300 + i * 60, 280 + i * 50, session.id)
                    )
                    conn.commit()
        
        print("   ✅ Test data created")
        
        # Test date range
        start_date = test_dates[0]
        end_date = test_dates[-1]
        date_range = DateRange(start_date, end_date)
        
        print("\n2. Testing CSV export...")
        csv_options = ExportOptions(
            format=ExportFormat.CSV,
            report_type=ReportType.DAILY_SUMMARY,
            date_range=date_range
        )
        
        csv_result = export_manager.export_data(csv_options)
        if csv_result.success:
            print(f"   ✅ CSV export successful: {os.path.basename(csv_result.filepath)}")
            print(f"   File size: {csv_result.metadata.get('file_size', 0)} bytes")
        else:
            print(f"   ❌ CSV export failed: {csv_result.error_message}")
        
        print("\n3. Testing JSON export...")
        json_options = ExportOptions(
            format=ExportFormat.JSON,
            report_type=ReportType.DETAILED_LOG,
            date_range=date_range,
            include_analytics=True
        )
        
        json_result = export_manager.export_data(json_options)
        if json_result.success:
            print(f"   ✅ JSON export successful: {os.path.basename(json_result.filepath)}")
            print(f"   File size: {json_result.metadata.get('file_size', 0)} bytes")
        else:
            print(f"   ❌ JSON export failed: {json_result.error_message}")
        
        print("\n4. Testing PDF export...")
        pdf_options = ExportOptions(
            format=ExportFormat.PDF,
            report_type=ReportType.PRODUCTIVITY_REPORT,
            date_range=date_range
        )
        
        pdf_result = export_manager.export_data(pdf_options)
        if pdf_result.success:
            print(f"   ✅ PDF export successful: {os.path.basename(pdf_result.filepath)}")
            print(f"   File size: {pdf_result.metadata.get('file_size', 0)} bytes")
        else:
            print(f"   ❌ PDF export failed: {pdf_result.error_message}")
        
        print("\n5. Testing export preview...")
        preview = export_manager.get_export_preview(csv_options)
        if 'error' not in preview:
            print("   ✅ Export preview generated:")
            print(f"      Date range: {preview['date_range']['start']} to {preview['date_range']['end']}")
            print(f"      Work sessions: {preview['data_counts']['work_sessions']}")
            print(f"      Work days: {preview['data_counts']['work_days']}")
            if 'statistics' in preview:
                print(f"      Total work hours: {preview['statistics']['total_work_hours']}")
        else:
            print(f"   ❌ Preview failed: {preview['error']}")
        
        print("\n6. Testing convenience methods...")
        
        # Test today export
        today_result = export_manager.export_today(ExportFormat.CSV)
        if today_result.success:
            print("   ✅ Today export successful")
        else:
            print(f"   ❌ Today export failed: {today_result.error_message}")
        
        # Test week export  
        week_result = export_manager.export_week(ExportFormat.JSON)
        if week_result.success:
            print("   ✅ Week export successful")
        else:
            print(f"   ❌ Week export failed: {week_result.error_message}")
        
        print("\n7. Testing validation...")
        
        # Test invalid date range
        valid, error = export_manager.validate_date_range(
            date.today() + timedelta(days=1),
            date.today() + timedelta(days=5)
        )
        if not valid:
            print("   ✅ Future date validation works:", error)
        else:
            print("   ❌ Future date validation failed")
        
        # Test valid date range
        valid, error = export_manager.validate_date_range(start_date, end_date)
        if valid:
            print("   ✅ Valid date range accepted")
        else:
            print(f"   ❌ Valid date range rejected: {error}")
        
        print("\n8. Checking generated files...")
        export_files = []
        if os.path.exists("exports"):
            export_files = [f for f in os.listdir("exports") if f.startswith("worklog_")]
            print(f"   ✅ Generated {len(export_files)} export files:")
            for file in export_files[:5]:  # Show first 5 files
                print(f"      - {file}")
        else:
            print("   ❌ No exports directory found")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        print("\n🧹 Test database cleaned up.")
        
        print("\n" + "=" * 60)
        print("🎉 Export functionality testing complete!")

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    test_export_functionality()