"""
Test script for Phase 2 revoke functionality.
This script tests the enhanced worklog manager with revoke capabilities.
"""

import sys
import os
from datetime import datetime, timedelta
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.worklog_manager import WorklogManager
from data.models import WorklogState, ActionType, BreakType
from utils.validators import WorklogValidator


def test_revoke_functionality():
    """Test the revoke functionality."""
    print("Testing Worklog Manager Phase 2 - Revoke Functionality")
    print("=" * 60)
    
    # Initialize worklog manager with test database
    wm = WorklogManager("test_revoke.db")
    validator = WorklogValidator()
    
    print("1. Testing normal workflow...")
    
    # Test normal workflow
    assert wm.start_day() == True
    assert wm.get_current_state() == WorklogState.WORKING
    print("   ✅ Started work day")
    
    time.sleep(1)  # Small delay to differentiate timestamps
    
    assert wm.stop_work(BreakType.COFFEE) == True
    assert wm.get_current_state() == WorklogState.ON_BREAK
    print("   ✅ Stopped for coffee break")
    
    time.sleep(1)
    
    assert wm.continue_work() == True
    assert wm.get_current_state() == WorklogState.WORKING
    print("   ✅ Continued work")
    
    time.sleep(1)
    
    assert wm.end_day() == True
    assert wm.get_current_state() == WorklogState.DAY_ENDED
    print("   ✅ Ended work day")
    
    print("\n2. Testing action history...")
    
    # Check action history
    history = wm.get_action_history()
    actions = history.get_revokable_actions()
    print(f"   📋 Total actions recorded: {len(actions)}")
    
    for i, action in enumerate(actions):
        print(f"   {i+1}. {action.action_type.value} at {action.timestamp.strftime('%H:%M:%S')}")
    
    print("\n3. Testing revoke validation...")
    
    # Test revoke validation
    if actions:
        last_action = actions[0]  # Most recent action
        is_valid, error = validator.validate_revoke_operation(history, last_action.id)
        print(f"   ✅ Can revoke last action: {is_valid}")
        if not is_valid:
            print(f"   ❌ Error: {error}")
    
    print("\n4. Testing revoke end day...")
    
    # Revoke end day
    if actions:
        end_day_action = next((a for a in actions if a.action_type == ActionType.END_DAY), None)
        if end_day_action:
            print(f"   🔄 Revoking end day action...")
            result = wm.revoke_action(end_day_action.id)
            print(f"   Result: {result}")
            print(f"   New state: {wm.get_current_state()}")
            
            if result:
                print("   ✅ Successfully revoked end day")
                assert wm.get_current_state() != WorklogState.DAY_ENDED
    
    print("\n5. Testing revoke continue...")
    
    # Revoke continue action
    actions = history.get_revokable_actions()
    continue_action = next((a for a in actions if a.action_type == ActionType.CONTINUE), None)
    if continue_action:
        print(f"   🔄 Revoking continue action...")
        result = wm.revoke_action(continue_action.id)
        print(f"   Result: {result}")
        print(f"   New state: {wm.get_current_state()}")
        
        if result:
            print("   ✅ Successfully revoked continue")
    
    print("\n6. Testing revoke stop...")
    
    # Revoke stop action
    actions = history.get_revokable_actions()
    stop_action = next((a for a in actions if a.action_type == ActionType.STOP), None)
    if stop_action:
        print(f"   🔄 Revoking stop action...")
        result = wm.revoke_action(stop_action.id)
        print(f"   Result: {result}")
        print(f"   New state: {wm.get_current_state()}")
        
        if result:
            print("   ✅ Successfully revoked stop")
    
    print("\n7. Testing revoke start day...")
    
    # Revoke start day
    actions = history.get_revokable_actions()
    start_action = next((a for a in actions if a.action_type == ActionType.START_DAY), None)
    if start_action:
        print(f"   🔄 Revoking start day action...")
        result = wm.revoke_action(start_action.id)
        print(f"   Result: {result}")
        print(f"   New state: {wm.get_current_state()}")
        
        if result:
            print("   ✅ Successfully revoked start day")
            assert wm.get_current_state() == WorklogState.NOT_STARTED
    
    print("\n8. Final action history...")
    
    # Show final history
    actions = history.get_revokable_actions()
    print(f"   📋 Remaining actions: {len(actions)}")
    
    all_actions = history.actions
    revoked_count = sum(1 for a in all_actions if a.revoked)
    print(f"   🚫 Revoked actions: {revoked_count}")
    
    print("\n9. Testing validation...")
    
    # Test various validation scenarios
    test_cases = [
        ("Valid state transition", 
         lambda: validator.validate_state_transition(WorklogState.NOT_STARTED, ActionType.START_DAY)),
        ("Invalid state transition", 
         lambda: validator.validate_state_transition(WorklogState.NOT_STARTED, ActionType.STOP)),
        ("Valid break type", 
         lambda: validator.validate_break_type(BreakType.LUNCH)),
        ("Valid work time", 
         lambda: validator.validate_work_time_limits(450)),
        ("Invalid work time", 
         lambda: validator.validate_work_time_limits(-10)),
    ]
    
    for test_name, test_func in test_cases:
        try:
            is_valid, error = test_func()
            status = "✅" if is_valid else "❌"
            print(f"   {status} {test_name}: {is_valid}")
            if not is_valid:
                print(f"     Error: {error}")
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 2 functionality testing complete!")
    
    # Cleanup
    wm.stop_timer()
    
    # Remove test database
    try:
        os.remove("test_revoke.db")
        print("🧹 Test database cleaned up.")
    except:
        pass


def test_break_tracking():
    """Test enhanced break tracking functionality."""
    print("\nTesting Enhanced Break Tracking")
    print("-" * 40)
    
    wm = WorklogManager("test_breaks.db")
    
    # Simulate a day with multiple breaks
    print("1. Simulating a full work day with breaks...")
    
    wm.start_day()
    time.sleep(0.1)
    
    # Morning work
    wm.stop_work(BreakType.COFFEE)
    time.sleep(0.1)
    wm.continue_work()
    time.sleep(0.1)
    
    # Lunch
    wm.stop_work(BreakType.LUNCH)
    time.sleep(0.1)
    wm.continue_work()
    time.sleep(0.1)
    
    # Afternoon break
    wm.stop_work(BreakType.GENERAL)
    time.sleep(0.1)
    wm.continue_work()
    time.sleep(0.1)
    
    # Another coffee
    wm.stop_work(BreakType.COFFEE)
    time.sleep(0.1)
    wm.continue_work()
    
    wm.end_day()
    
    # Check break data
    if wm.current_session:
        breaks = wm.db.get_session_breaks(wm.current_session.id)
        print(f"   📊 Total breaks: {len(breaks)}")
        
        break_counts = {}
        for break_period in breaks:
            break_type = break_period.break_type.value
            break_counts[break_type] = break_counts.get(break_type, 0) + 1
        
        for break_type, count in break_counts.items():
            print(f"   {break_type.title()}: {count} breaks")
    
    print("   ✅ Break tracking test complete")
    
    # Cleanup
    wm.stop_timer()
    try:
        os.remove("test_breaks.db")
    except:
        pass


if __name__ == "__main__":
    test_revoke_functionality()
    test_break_tracking()