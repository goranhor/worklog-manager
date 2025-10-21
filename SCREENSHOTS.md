# Screenshots

Visual guide to Worklog Manager's interface and features.

## Main Interface

### Application Window
*Main application window showing time tracking interface*

**Features visible:**
- Real-time timer display
- Status indicators
- Control buttons (Start Day, Stop, Continue, End Day)
- Time summary panel
- Break type selector

### Color-Coded Status

**Status Indicators:**
- 🟢 **Green** - Meeting or exceeding work targets
- 🟠 **Orange** - Approaching targets or warnings
- 🔴 **Red** - Overtime or critical status
- 🔵 **Blue** - Current active session

## Time Tracking

### Starting the Day
*Screenshot showing "Start Day" button and initial state*

### Active Work Session
*Screenshot showing running timer and "Working" status*

### Break Period
*Screenshot showing break selection and "On Break" status*

### End of Day Summary
*Screenshot showing completed day with time summary*

## Features

### Action History & Revoke
*Screenshot showing action history dialog with revoke options*

**Displays:**
- List of recent actions (up to 5)
- Timestamps for each action
- Confirmation before rollback

### Export Dialog
*Screenshot showing export options dialog*

**Options:**
- Format selection (CSV, JSON, PDF)
- Date range picker
- Quick export shortcuts

### Settings Dialog
*Screenshot showing settings configuration*

**Sections:**
- Work norm configuration
- Theme selection (Light/Dark)
- Notification preferences
- Backup settings
- Keyboard shortcuts

## Themes

### Light Theme
*Screenshot showing light theme appearance*

### Dark Theme
*Screenshot showing dark theme appearance*

## System Tray Integration

### Tray Icon
*Screenshot showing system tray icon and menu*

**Menu Options:**
- Quick actions
- Show/Hide window
- Exit application

## Notifications

### Break Reminder
*Screenshot showing break reminder notification*

### Overtime Alert
*Screenshot showing overtime warning notification*

### Work Complete
*Screenshot showing work norm completion notification*

## Reports

### CSV Export Sample
```csv
Date,Start Time,End Time,Total Work,Breaks,Productive Time,Overtime
2025-10-21,08:00:00,17:30:00,09:30:00,01:00:00,08:30:00,01:00:00
```

### JSON Export Sample
```json
{
  "export_date": "2025-10-21",
  "work_sessions": [...],
  "statistics": {
    "total_work_time": 510,
    "overtime": 60
  }
}
```

## Time Summary Panel

### Detailed View
*Screenshot showing expanded time summary*

**Metrics displayed:**
- Current Session: Active work time
- Total Work Time: All work periods
- Break Time: All breaks combined
- Productive Time: Net work time
- Remaining: Time to reach norm
- Overtime: Time beyond norm

## Error Handling

### User-Friendly Error Messages
*Screenshot showing error dialog with helpful message*

### Validation Warnings
*Screenshot showing input validation warning*

## Data Management

### Reset Day Confirmation
*Screenshot showing double-confirmation dialog for reset*

### Backup Notification
*Screenshot showing automatic backup notification*

---

## Adding Screenshots

To contribute screenshots:

1. Take clear, high-resolution screenshots (1280x720 or higher)
2. Annotate important features if needed
3. Save as PNG format
4. Add to `docs/images/` directory
5. Update this file with image references

**Example:**
```markdown
![Main Window](docs/images/main-window.png)
*Main application window*
```

---

**Note:** Screenshots will be added as the project documentation evolves. Contributors are welcome to submit screenshots following the guidelines above.
