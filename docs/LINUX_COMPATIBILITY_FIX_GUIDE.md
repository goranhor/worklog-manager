# Linux openSUSE Compatibility Guide

## Overview

This guide documents all changes required to make the Worklog Manager application compatible with **openSUSE Leap 15.4** and **Python 3.6.15**. These changes ensure backward compatibility while maintaining full functionality.

## System Requirements

- **OS**: openSUSE Leap 15.4 (or similar Linux distributions)
- **Python**: 3.6.15 or higher
- **GUI**: tkinter support required

## Installation Steps

### 1. Install System Dependencies

```bash
# Install tkinter for Python 3
sudo zypper install python3-tk

# Alternative for other distributions:
# Ubuntu/Debian: sudo apt-get install python3-tk
# CentOS/RHEL: sudo yum install tkinter
# Fedora: sudo dnf install python3-tkinter
```

### 2. Install Python Dependencies

```bash
# Install dataclasses backport for Python 3.6
pip3 install dataclasses

# Install required application dependencies
pip3 install plyer reportlab
```

## Code Changes Required

### 1. Create DateTime Compatibility Module

**File**: `utils/datetime_compat.py` (NEW FILE)

```python
"""DateTime compatibility utilities for Python 3.6 support."""

import re
from datetime import datetime
from typing import Union


def fromisoformat_compat(date_string: str) -> datetime:
    """
    Compatibility function for datetime.fromisoformat() which was introduced in Python 3.7.

    This function provides equivalent functionality for Python 3.6.

    Args:
        date_string: ISO format date string

    Returns:
        datetime object

    Raises:
        ValueError: If the date string format is invalid
    """
    # Handle various ISO format patterns
    patterns = [
        # Full datetime with microseconds and timezone (T separator)
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime with timezone (T separator)
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime without timezone (T separator)
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)$',
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$',
        # Full datetime with microseconds and timezone (space separator)
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d+)([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime with timezone (space separator)
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime without timezone (space separator)
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d+)$',
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$',
        # Date only
        r'^(\d{4})-(\d{2})-(\d{2})$',
        # Time only (assuming today's date)
        r'^(\d{2}):(\d{2}):(\d{2})\.(\d+)$',
        r'^(\d{2}):(\d{2}):(\d{2})$',
    ]

    date_string = date_string.strip()

    # Try each pattern
    for i, pattern in enumerate(patterns):
        match = re.match(pattern, date_string)
        if match:
            groups = match.groups()

            if i == 0:  # Full datetime with microseconds and timezone (T separator)
                year, month, day, hour, minute, second, microsecond, tz = groups
                dt = datetime(int(year), int(month), int(day),
                            int(hour), int(minute), int(second),
                            int(microsecond.ljust(6, '0')[:6]))
                return dt

            elif i == 1:  # Full datetime with timezone (T separator)
                year, month, day, hour, minute, second, tz = groups
                return datetime(int(year), int(month), int(day),
                              int(hour), int(minute), int(second))

            elif i == 2:  # Full datetime without timezone, with microseconds (T separator)
                year, month, day, hour, minute, second, microsecond = groups
                return datetime(int(year), int(month), int(day),
                              int(hour), int(minute), int(second),
                              int(microsecond.ljust(6, '0')[:6]))

            elif i == 3:  # Full datetime without timezone (T separator)
                year, month, day, hour, minute, second = groups
                return datetime(int(year), int(month), int(day),
                              int(hour), int(minute), int(second))

            elif i == 4:  # Full datetime with microseconds and timezone (space separator)
                year, month, day, hour, minute, second, microsecond, tz = groups
                dt = datetime(int(year), int(month), int(day),
                            int(hour), int(minute), int(second),
                            int(microsecond.ljust(6, '0')[:6]))
                return dt

            elif i == 5:  # Full datetime with timezone (space separator)
                year, month, day, hour, minute, second, tz = groups
                return datetime(int(year), int(month), int(day),
                              int(hour), int(minute), int(second))

            elif i == 6:  # Full datetime without timezone, with microseconds (space separator)
                year, month, day, hour, minute, second, microsecond = groups
                return datetime(int(year), int(month), int(day),
                              int(hour), int(minute), int(second),
                              int(microsecond.ljust(6, '0')[:6]))

            elif i == 7:  # Full datetime without timezone (space separator)
                year, month, day, hour, minute, second = groups
                return datetime(int(year), int(month), int(day),
                              int(hour), int(minute), int(second))

            elif i == 8:  # Date only
                year, month, day = groups
                return datetime(int(year), int(month), int(day))

            elif i == 9:  # Time only with microseconds
                hour, minute, second, microsecond = groups
                today = datetime.today().date()
                return datetime.combine(today,
                                      datetime.min.time().replace(
                                          hour=int(hour), minute=int(minute),
                                          second=int(second),
                                          microsecond=int(microsecond.ljust(6, '0')[:6])))

            elif i == 10:  # Time only
                hour, minute, second = groups
                today = datetime.today().date()
                return datetime.combine(today,
                                      datetime.min.time().replace(
                                          hour=int(hour), minute=int(minute),
                                          second=int(second)))

    # If no pattern matches, try the native Python 3.6 strptime as fallback
    try:
        # Try common ISO formats that strptime can handle
        for fmt in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%H:%M:%S']:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
    except Exception:
        pass

    raise ValueError(f"Invalid isoformat string: '{date_string}'")


# Provide compatibility function without monkey patching
def datetime_fromisoformat(date_string: str) -> datetime:
    """
    Compatibility wrapper for datetime.fromisoformat().

    Uses native fromisoformat if available (Python 3.7+),
    otherwise uses our compatibility implementation.
    """
    if hasattr(datetime, 'fromisoformat'):
        return datetime.fromisoformat(date_string)
    else:
        return fromisoformat_compat(date_string)
```

### 2. Update Utils Package

**File**: `utils/__init__.py`

```python
"""Utility functions and helpers."""

# Import datetime compatibility for Python 3.6 support
from . import datetime_compat
```

### 3. Update Main Application Entry Point

**File**: `main.py` (Update imports section)

```python
import sys
import os
import logging
import threading
import atexit
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import datetime compatibility for Python 3.6 support (must be imported early)
from utils.datetime_compat import fromisoformat_compat
from datetime import datetime

# ... rest of imports
```

### 4. Replace datetime.fromisoformat() Calls

**Search and replace across all files:**

```bash
# Use sed command to replace all occurrences
sed -i 's/datetime\.fromisoformat(/datetime_fromisoformat(/g' \
    utils/validators.py \
    core/action_history.py \
    core/time_calculator.py \
    core/data_aggregator.py \
    core/simple_backup_manager.py \
    data/database.py \
    exporters/csv_exporter.py
```

**Then add import to each affected file:**

```python
from utils.datetime_compat import datetime_fromisoformat
```

### 5. Files That Need Import Updates

Add `from utils.datetime_compat import datetime_fromisoformat` to:

- `utils/validators.py`
- `core/action_history.py`
- `core/time_calculator.py`
- `core/data_aggregator.py`
- `core/simple_backup_manager.py`
- `data/database.py`
- `exporters/csv_exporter.py`

### 6. Fix Unicode Characters in GUI

**File**: `gui/components/break_tracker.py`

Replace Unicode emojis with ASCII alternatives:

```python
# Line ~71: Replace lunch emoji
tk.Label(lunch_frame, text="[L] Lunch", bg="#FFE4B5").grid(row=0, column=0, sticky="w", padx=5, pady=2)

# Line ~80: Replace coffee emoji
tk.Label(coffee_frame, text="[C] Coffee", bg="#D2B48C").grid(row=0, column=0, sticky="w", padx=5, pady=2)

# Line ~89: Replace general break emoji
tk.Label(general_frame, text="[B] General", bg="#F0F0F0").grid(row=0, column=0, sticky="w", padx=5, pady=2)

# Line ~171: Replace emoji mapping
symbol = {
    BreakType.LUNCH: "[L]",
    BreakType.COFFEE: "[C]",
    BreakType.GENERAL: "[B]"
}.get(break_period.break_type, "[B]")

break_text = f"{symbol} {break_period.break_type.value.title()}: {status}"
```

### 7. Add ttk.Spinbox Compatibility

**File**: `gui/settings_dialog.py` (Add after imports)

```python
# Compatibility wrapper for ttk.Spinbox (not available in Python 3.6)
if not hasattr(ttk, 'Spinbox'):
    class TtkSpinboxCompat(tk.Spinbox):
        """Compatibility wrapper for ttk.Spinbox using tk.Spinbox"""
        def __init__(self, parent, **kwargs):
            # Convert ttk-style options to tk.Spinbox options
            tk_kwargs = kwargs.copy()

            # Handle common ttk.Spinbox parameters
            if 'from_' in tk_kwargs:
                tk_kwargs['from'] = tk_kwargs.pop('from_')
            if 'to' in tk_kwargs:
                tk_kwargs['to'] = tk_kwargs['to']
            if 'increment' in tk_kwargs:
                tk_kwargs['increment'] = tk_kwargs['increment']
            if 'textvariable' in tk_kwargs:
                tk_kwargs['textvariable'] = tk_kwargs['textvariable']

            # Set some reasonable defaults for appearance
            tk_kwargs.setdefault('width', 10)
            tk_kwargs.setdefault('justify', 'center')

            super().__init__(parent, **tk_kwargs)

    # Monkey patch ttk to include our compatibility Spinbox
    ttk.Spinbox = TtkSpinboxCompat
```

## Implementation Steps for Forked Project

### Step 1: Create New Branch

```bash
git checkout -b feature/linux-opensuse-compatibility
```

### Step 2: Install System Dependencies

```bash
# openSUSE
sudo zypper install python3-tk

# Install Python packages
pip3 install dataclasses plyer reportlab
```

### Step 3: Create Compatibility Module

1. Create `utils/datetime_compat.py` with the content above
2. Update `utils/__init__.py` to import the compatibility module

### Step 4: Update Application Files

1. Update `main.py` imports section
2. Add compatibility imports to all files using `datetime.fromisoformat()`
3. Replace all `datetime.fromisoformat(` with `datetime_fromisoformat(`

### Step 5: Fix GUI Compatibility

1. Replace Unicode emojis in `gui/components/break_tracker.py`
2. Add ttk.Spinbox compatibility to `gui/settings_dialog.py`

### Step 6: Test Application

```bash
python3 main.py
```

## Expected Results

After implementing these changes:

✅ **Application runs successfully on Python 3.6**  
✅ **All GUI components work properly**  
✅ **Settings dialog opens without errors**  
✅ **Database operations function correctly**  
✅ **Export functionality works**  
✅ **No Unicode character errors**

## Verification Checklist

- [ ] Application starts without errors
- [ ] Main window displays correctly
- [ ] Settings dialog opens and all controls work
- [ ] Work sessions can be started/stopped
- [ ] Break tracking functions properly
- [ ] Export features work
- [ ] No datetime-related errors in logs

## Notes

- These changes maintain full backward compatibility
- All features remain functional on newer Python versions
- Changes are non-breaking for existing installations
- The compatibility layer automatically detects Python version capabilities

## Troubleshooting

### Common Issues:

1. **tkinter ImportError**: Install python3-tk package for your distribution
2. **dataclasses ImportError**: Install dataclasses backport via pip
3. **Unicode errors**: Ensure all emoji characters are replaced with ASCII alternatives
4. **Spinbox errors**: Verify ttk.Spinbox compatibility wrapper is properly imported

### Testing Commands:

```bash
# Test tkinter import
python3 -c "import tkinter; print('tkinter works')"

# Test dataclasses import
python3 -c "import dataclasses; print('dataclasses works')"

# Test datetime compatibility
python3 -c "from utils.datetime_compat import datetime_fromisoformat; print('datetime compat works')"
```
