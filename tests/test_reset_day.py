#!/usr/bin/env python3
"""Test script for Reset Day functionality."""

import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.worklog_manager import WorklogManager
from data.models import WorklogState, BreakType

def test_reset_day():
    """Test the reset day functionality."""
    print("Testing Reset Day Functionality")
    print("=" * 50)
    
    # Create worklog manager with test database
    test_db_path = "test_reset.db"
    
    # Clean up any existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    try:
        manager = WorklogManager(test_db_path)
        
        print("1. Starting a normal work day...")
        success = manager.start_day()
        print(f"   ✅ Started day: {success}")
        print(f"   State: {manager.get_current_state()}")
        
        print("\n2. Taking a coffee break...")
        success = manager.stop_work(BreakType.COFFEE)
        print(f"   ✅ Stopped for coffee: {success}")
        print(f"   State: {manager.get_current_state()}")
        
        print("\n3. Continuing work...")
        success = manager.continue_work()
        print(f"   ✅ Continued work: {success}")
        print(f"   State: {manager.get_current_state()}")
        
        print("\n4. Checking session data before reset...")
        session = manager.current_session
        if session:
            print(f"   Session ID: {session.id}")
            print(f"   Start time: {session.start_time}")
            
        print("\n5. Checking action history before reset...")
        history = manager.get_action_history()
        actions_before = len(history.get_revokable_actions())
        print(f"   Actions in history: {actions_before}")
        
        print("\n6. Resetting the day...")
        success = manager.reset_day()
        print(f"   ✅ Reset successful: {success}")
        print(f"   New state: {manager.get_current_state()}")
        
        print("\n7. Verifying reset results...")
        
        # Check state
        if manager.get_current_state() == WorklogState.NOT_STARTED:
            print("   ✅ State correctly reset to NOT_STARTED")
        else:
            print(f"   ❌ State not reset correctly: {manager.get_current_state()}")
        
        # Check action history
        history_after = manager.get_action_history()
        actions_after = len(history_after.get_revokable_actions())
        if actions_after == 0:
            print("   ✅ Action history cleared")
        else:
            print(f"   ❌ Action history not cleared: {actions_after} actions remain")
        
        # Check session
        new_session = manager.current_session
        if new_session and new_session.id != session.id:
            print("   ✅ New session created")
        else:
            print("   ❌ Session not properly reset")
        
        print("\n8. Testing fresh start after reset...")
        success = manager.start_day()
        print(f"   ✅ Can start new day: {success}")
        print(f"   New state: {manager.get_current_state()}")
        
        print("\n9. Final verification...")
        calculations = manager.get_current_calculations()
        print(f"   Total work time: {calculations.total_work_minutes} minutes")
        print(f"   Total breaks: {calculations.total_break_minutes} minutes")
        
        if calculations.total_work_minutes >= 0 and calculations.total_break_minutes == 0:
            print("   ✅ Fresh session calculations look correct")
        else:
            print("   ❌ Session calculations seem incorrect")
            
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
    
    print("\n" + "=" * 50)
    print("🎉 Reset Day functionality test complete!")
    return True

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    test_reset_day()