"""
Test script for Worklog Manager core functionality.
This script tests the main features without GUI.
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.worklog_manager import WorklogManager
from data.models import WorklogState, ActionType, BreakType


def test_worklog_functionality():
    """Test core worklog functionality."""
    print("Testing Worklog Manager Core Functionality")
    print("=" * 50)
    
    # Initialize worklog manager with test database
    wm = WorklogManager("test_worklog.db")
    
    # Test 1: Check initial state
    print(f"1. Initial state: {wm.get_current_state()}")
    assert wm.get_current_state() == WorklogState.NOT_STARTED
    
    # Test 2: Start day
    print("2. Starting work day...")
    result = wm.start_day()
    print(f"   Result: {result}")
    print(f"   State: {wm.get_current_state()}")
    assert result == True
    assert wm.get_current_state() == WorklogState.WORKING
    
    # Test 3: Get calculations
    print("3. Getting time calculations...")
    calc = wm.get_current_calculations()
    print(f"   Work time: {calc.total_work_minutes} minutes")
    print(f"   Remaining: {calc.remaining_minutes} minutes")
    print(f"   Overtime: {calc.overtime_minutes} minutes")
    
    # Test 4: Stop for lunch break
    print("4. Stopping for lunch break...")
    result = wm.stop_work(BreakType.LUNCH)
    print(f"   Result: {result}")
    print(f"   State: {wm.get_current_state()}")
    assert result == True
    assert wm.get_current_state() == WorklogState.ON_BREAK
    
    # Test 5: Continue work
    print("5. Continuing work...")
    result = wm.continue_work()
    print(f"   Result: {result}")
    print(f"   State: {wm.get_current_state()}")
    assert result == True
    assert wm.get_current_state() == WorklogState.WORKING
    
    # Test 6: End day
    print("6. Ending work day...")
    result = wm.end_day()
    print(f"   Result: {result}")
    print(f"   State: {wm.get_current_state()}")
    assert result == True
    assert wm.get_current_state() == WorklogState.DAY_ENDED
    
    # Test 7: Final calculations
    print("7. Final calculations...")
    calc = wm.get_current_calculations()
    print(f"   Total work: {calc.total_work_minutes} minutes")
    print(f"   Total breaks: {calc.total_break_minutes} minutes")
    print(f"   Productive: {calc.productive_minutes} minutes")
    print(f"   Overtime: {calc.overtime_minutes} minutes")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Core functionality working correctly.")
    
    # Cleanup
    wm.stop_timer()
    
    # Remove test database
    try:
        os.remove("test_worklog.db")
        print("🧹 Test database cleaned up.")
    except:
        pass


if __name__ == "__main__":
    test_worklog_functionality()