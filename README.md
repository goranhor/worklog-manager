# Worklog Manager

A comprehensive Python GUI application for tracking daily work hours with automatic calculation of productive time, breaks, and overtime. Designed to ensure compliance with a 7.5-hour work day norm while providing detailed logging and reporting capabilities.

## Features

### ✅ Core Time Tracking
- **Start Day**: Begin worklog for current date
- **Stop**: Pause work when leaving workplace
- **Continue**: Resume work when returning
- **End Day**: Complete daily logging with calculations
- **Real-time Timer**: Live tracking with 1-second precision

### ✅ Break Management
- **Multiple Break Types**: Lunch, Coffee, and General breaks
- **Automatic Tracking**: Duration calculation for all breaks
- **Visual Selection**: Easy break type selection interface

### ✅ Time Calculations
- **Work Norm Compliance**: 7.5-hour (450 minutes) daily target
- **Productive Time**: Total work time tracking
- **Overtime Calculation**: Automatic overtime detection
- **Remaining Time**: Live countdown to work norm completion
- **Color-coded Status**: Visual indicators for time status

### ✅ Data Management
- **SQLite Database**: Reliable local data storage
- **Action Logging**: Complete audit trail of all actions
- **Daily Log Files**: Organized by date (day.month.year)
- **Automatic Backup**: Daily database backups

### ✅ Revoke System (Phase 2)
- **Action History**: Complete tracking of all work day actions with timestamps
- **Intelligent Revoke**: Undo the last 5 actions with full state restoration
- **Visual Confirmation**: Dialog shows exactly what will be undone with action details
- **Safe Operations**: Comprehensive validation prevents invalid state transitions
- **Enhanced Break Tracking**: Visual indicators, emoji status, and recent break history
- **Real-time Validation**: Input validation with helpful error messages
- **Reset Day**: Complete day reset functionality with double confirmation safety

### ✅ Export & Reporting (Phase 3)
- **Multiple Formats**: CSV, JSON, and PDF export capabilities
- **Report Types**: Daily summary, detailed logs, break analysis, productivity reports
- **Date Range Support**: Export today, this week, custom ranges up to 1 year
- **Analytics Integration**: Productivity trends, statistics, and insights
- **Professional Output**: Formatted reports with metadata and summary statistics
- **Quick Export Options**: One-click export for common scenarios
- **File Management**: Automatic file naming and organized export directory

### ✅ Advanced Features (Phase 4) - COMPLETED
- **Settings Management**: Comprehensive configuration system with persistent settings
- **Theme System**: Light/Dark themes with custom color schemes and visual preferences
- **Notification System**: Work reminders, break alerts, overtime warnings with cross-platform support
- **Automatic Backup System**: Scheduled database backups with configurable retention policies
- **Keyboard Shortcuts**: Customizable hotkeys for all major application functions
- **System Tray Integration**: Minimize to system tray with quick actions and notifications
- **Help System**: Built-in documentation, tutorials, and contextual help
- **Cross-Platform Support**: Enhanced compatibility for Windows, macOS, and Linux
- **Advanced Settings**: Customizable preferences and work norms
- **Additional Report Types**: Monthly summaries, yearly analysis
- **Chart Generation**: Visual productivity charts and graphs

## Installation

### Prerequisites
- Python 3.7 or higher
- All dependencies are part of Python standard library (no external packages required)

### Setup
1. Clone or download the project:
   ```bash
   git clone <repository-url>
   cd worklog-manager
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Starting Your Work Day
1. Launch the application
2. Click **"Start Day"** to begin tracking
3. The timer will start running and display current session time

### Taking Breaks
1. Select break type (Lunch, Coffee, or General)
2. Click **"Stop"** when leaving your workspace
3. Break time is automatically tracked
4. Click **"Continue"** when returning to work

### Ending Your Day
1. Click **"End Day"** when finished working
2. Review the summary showing:
   - Total productive time
   - Overtime or remaining time
   - Break time breakdown
3. Confirm to save the day's data

### Using the Revoke System
1. Click **"Revoke Last Action"** button (enabled when actions are available)
2. Review the action history in the revoke dialog
3. Select which actions you want to undo (up to last 5)
4. Confirm to rollback - the application state will be restored
5. All related data (timers, database records) are automatically updated

### Resetting the Day
1. Click **"Reset Day"** button to completely clear today's data
2. Review the warning - this action permanently deletes ALL today's data
3. Confirm twice for safety (this cannot be undone!)
4. The application will return to a fresh "Not Started" state
5. You can immediately begin a new work day

**When to Use Reset Day:**
- Made multiple mistakes that can't be fixed with revoke
- Testing the application and want a clean slate
- Started tracking incorrectly and prefer to restart
- Database corruption or data inconsistencies
- **⚠️ WARNING**: This permanently deletes ALL today's data!

### Exporting Your Data
1. Click **"Export Data"** button to access export options
2. Choose from quick export options:
   - **Yes**: Export today's data as CSV
   - **No**: Export this week's data as JSON
   - **Cancel**: Choose custom file location and format
3. For custom exports, select file type (CSV, JSON, PDF) via file extension
4. Data is automatically exported with professional formatting
5. Option to open the exports folder after successful export

**Available Export Formats:**
- **CSV**: Spreadsheet-compatible tabular data with summaries
- **JSON**: Structured data with complete metadata and analytics
- **PDF**: Professional formatted reports (requires ReportLab library)

**Export Content Includes:**
- Daily work summaries with productivity metrics
- Break analysis and patterns
- Time calculations and overtime tracking
- Action logs and session details
- Statistical trends and insights

### Understanding the Display

#### Time Summary Panel
- **Current Session**: Active work time since last start/continue
- **Total Work Time**: All work periods combined
- **Break Time**: All break periods combined  
- **Productive Time**: Net work time (same as Total Work Time)
- **Remaining**: Time left to reach 7.5-hour norm
- **Overtime**: Time exceeding the 7.5-hour norm

#### Color Indicators
- **Green**: Meeting or exceeding work targets
- **Orange**: Approaching targets or warnings
- **Red**: Overtime or critical status
- **Blue**: Current active session highlighting

## File Structure

```
worklog-manager/
├── main.py                     # Application entry point
├── config.ini                  # Configuration file
├── requirements.txt            # Dependencies (none required)
├── gui/                        # GUI components
│   ├── main_window.py          # Main application window
│   └── components/
│       └── timer_display.py    # Real-time timer display
├── core/                       # Business logic
│   ├── worklog_manager.py      # Main worklog management
│   └── time_calculator.py      # Time calculation utilities
├── data/                       # Data management
│   ├── database.py             # SQLite operations
│   └── models.py               # Data models
├── logs/                       # Application logs
├── exports/                    # Exported reports
└── docs/                       # Documentation
    ├── IMPLEMENTATION_PLAN.md
    ├── TECHNICAL_SPECIFICATION.md
    └── USER_REQUIREMENTS.md
```

## Database Schema

The application uses SQLite with three main tables:

### work_sessions
- Stores daily work session summaries
- Tracks total times and status for each date

### action_log  
- Records every user action with timestamps
- Provides complete audit trail for revoke functionality

### break_periods
- Tracks individual break periods
- Categorizes breaks by type with duration calculation

## Configuration

Edit `config.ini` to customize:
- Work norm hours (default: 7.5)
- Timer update frequency
- UI theme and colors
- Backup and logging settings

## Logging

The application creates daily log files in the `logs/` directory:
- Format: `worklog_YYYYMMDD.log`
- Logs all actions, errors, and system events
- Configurable log levels in `config.ini`

## Data Export

*Coming in Phase 3*

Export your work data in multiple formats:
- **CSV**: For spreadsheet analysis
- **JSON**: For data processing
- **PDF**: For human-readable reports

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Check Python version (3.7+ required)
   - Verify file permissions in application directory

2. **Database errors**
   - Check disk space
   - Verify write permissions
   - Review log files for details

3. **Timer not updating**
   - Restart the application
   - Check system clock settings

4. **Data not saving**
   - Verify database file permissions
   - Check available disk space
   - Review error logs

### Log Files
Check the `logs/` directory for detailed error information:
```bash
tail -f logs/worklog_YYYYMMDD.log
```

## Support

For issues or questions:
1. Check the log files for error details
2. Review this README for common solutions
3. Verify your configuration settings
4. Ensure Python version compatibility

## Version History

### v1.0.0 (Current - Phase 1)
- ✅ Core time tracking functionality
- ✅ Real-time timer and calculations
- ✅ Break management system
- ✅ SQLite database storage
- ✅ Basic GUI with all essential controls

### Upcoming Releases
- **v1.1.0**: Revoke/Undo system (Phase 2)
- **v1.2.0**: Export and reporting (Phase 3)
- **v1.3.0**: Advanced features and polish (Phase 4)

## License

This project is developed for personal/company use. All rights reserved.

---

**Worklog Manager v1.0.0** - Professional time tracking for productive workdays.