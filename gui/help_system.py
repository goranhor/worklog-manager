"""
Integrated Help System for Worklog Manager Application

Provides comprehensive help documentation, tooltips, user guides, and contextual help.
Includes interactive tutorials and getting started wizards.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List, Optional, Tuple
import webbrowser
from dataclasses import dataclass
import json
import os

@dataclass
class HelpTopic:
    """Represents a help topic with content and metadata."""
    id: str
    title: str
    content: str
    category: str
    keywords: List[str]
    related_topics: List[str]
    difficulty: str = "beginner"  # beginner, intermediate, advanced

class HelpSystem:
    """Main help system manager."""
    
    def __init__(self):
        self.topics: Dict[str, HelpTopic] = {}
        self.categories: Dict[str, List[str]] = {}
        self.load_help_content()
    
    def load_help_content(self):
        """Load help content and organize by categories."""
        # Define help topics
        topics_data = [
            {
                'id': 'getting_started',
                'title': 'Getting Started',
                'category': 'Basics',
                'keywords': ['start', 'begin', 'first', 'setup', 'introduction'],
                'related_topics': ['work_tracking', 'break_management'],
                'content': '''
# Getting Started with Worklog Manager

Welcome to Worklog Manager! This guide will help you get started with tracking your work hours and managing your daily productivity.

## First Steps

1. **Start Your First Work Session**
   - Click the "Start Work" button to begin tracking your time
   - The timer will show your current work session duration
   - Your work status will be displayed in the main window

2. **Monitor Your Progress**
   - The application tracks toward a standard 7.5-hour work day
   - Progress bars show your completion status
   - Color coding indicates if you're on track, ahead, or behind schedule

3. **Take Breaks When Needed**
   - Click "Take Break" to pause work tracking
   - Break time is tracked separately from work time
   - The app will remind you when breaks are getting too long

4. **End Your Work Day**
   - Click "End Work" when you're finished for the day
   - Review your daily summary to see total hours and break time
   - Your data is automatically saved

## Key Features

- **Automatic Time Tracking**: Precise tracking of work and break periods
- **7.5 Hour Work Norm**: Built-in standard for full work days
- **Break Management**: Monitors break duration and frequency
- **Action History**: View and revoke recent actions if needed
- **Export Capabilities**: Save your data in multiple formats
- **System Tray Integration**: Work in the background with tray notifications

## Tips for Success

- Start your work session as soon as you begin working
- Use the break feature for legitimate breaks (lunch, coffee, etc.)
- Review your daily summary to identify productivity patterns
- Configure notifications to remind you about work start/end times
- Use keyboard shortcuts for quick actions

Next: Learn about [Work Tracking Basics](work_tracking) or [Break Management](break_management)
'''
            },
            {
                'id': 'work_tracking',
                'title': 'Work Time Tracking',
                'category': 'Core Features',
                'keywords': ['work', 'time', 'tracking', 'hours', 'session'],
                'related_topics': ['getting_started', 'break_management', 'daily_summary'],
                'content': '''
# Work Time Tracking

The core feature of Worklog Manager is precise work time tracking with intelligent monitoring and reporting.

## Starting and Stopping Work

### Start Work Session
- Click "Start Work" button or use keyboard shortcut (Ctrl+Shift+S)
- Timer immediately begins counting
- Status changes to "Working"
- System tray icon updates to show active status

### End Work Session
- Click "End Work" button or use keyboard shortcut (Ctrl+Shift+E)
- Final work duration is calculated and saved
- Session is added to your work history
- Daily totals are updated

## Understanding Work Norms

### 7.5 Hour Standard
- Default work day target is 7.5 hours (450 minutes)
- Progress bars show completion percentage
- Visual indicators show if you're on track

### Overtime Detection
- Automatic warnings when approaching overtime (configurable)
- Different color coding for overtime hours
- Notifications can alert you to long work sessions

## Work Session Management

### Active Session Monitoring
- Real-time display of current session duration
- Running total for the day
- Time remaining to reach daily goal

### Session History
- Complete log of all work sessions
- Start and end times for each session
- Duration calculations
- Daily, weekly, and monthly summaries

## Customizing Work Norms

Access Settings > Work Norms to customize:
- Daily hour targets (default 7.5 hours)
- Overtime threshold settings
- Warning time preferences
- Break duration limits

## Tips for Accurate Tracking

1. **Start Immediately**: Begin tracking as soon as you start working
2. **Use Breaks Properly**: Don't forget to use break mode for non-work time
3. **End Sessions**: Always end your work session when stopping
4. **Review Daily**: Check your daily summary for accuracy
5. **Adjust Settings**: Customize work norms to match your schedule

Related Topics: [Break Management](break_management), [Daily Summary](daily_summary), [Settings Configuration](settings)
'''
            },
            {
                'id': 'break_management',
                'title': 'Break Management',
                'category': 'Core Features',
                'keywords': ['break', 'pause', 'lunch', 'coffee', 'rest'],
                'related_topics': ['work_tracking', 'getting_started', 'notifications'],
                'content': '''
# Break Management

Proper break management is essential for maintaining productivity and work-life balance. Worklog Manager provides comprehensive break tracking and management features.

## Taking Breaks

### Start a Break
- Click "Take Break" button during an active work session
- Or use keyboard shortcut (Ctrl+Shift+B)
- Work timer pauses, break timer starts
- Status changes to "On Break"

### End a Break
- Click "End Break" button to resume work
- Or use keyboard shortcut (Ctrl+Shift+R)
- Break duration is recorded
- Work timer resumes from where it left off

## Break Types and Limits

### Default Break Settings
- Maximum single break: 60 minutes (configurable)
- Daily break limit: 120 minutes total (configurable)
- Automatic warnings for long breaks

### Break Categories
The system tracks different types of breaks:
- **Short Breaks**: Under 15 minutes (coffee, restroom)
- **Medium Breaks**: 15-45 minutes (lunch, personal calls)
- **Long Breaks**: Over 45 minutes (extended lunch, appointments)

## Break Monitoring

### Visual Indicators
- Break duration timer shows current break length
- Color changes warn about approaching limits
- Daily break total displayed in summary

### Automatic Reminders
Configure in Settings > Notifications:
- Break reminder intervals (default: every 90 minutes of work)
- Long break warnings (when breaks exceed set limits)
- Return to work reminders

## Break History and Analysis

### Break Tracking
- Complete log of all break periods
- Duration and timing analysis
- Daily and weekly break patterns
- Integration with work session data

### Break Reports
- Average break duration
- Most common break times
- Break frequency analysis
- Impact on daily productivity

## Best Practices for Breaks

1. **Regular Short Breaks**: Take 5-10 minute breaks every hour
2. **Proper Lunch Breaks**: Allow 30-60 minutes for meals
3. **Avoid Extended Breaks**: Keep non-meal breaks under 15 minutes
4. **Use Break Mode**: Always activate break mode when stepping away
5. **Review Patterns**: Check break reports to optimize your schedule

## Configuring Break Settings

Access Settings > Work Norms to adjust:
- Maximum break duration per session
- Daily total break limits
- Warning thresholds
- Break reminder intervals

Related Topics: [Work Tracking](work_tracking), [Notifications](notifications), [Daily Summary](daily_summary)
'''
            },
            {
                'id': 'daily_summary',
                'title': 'Daily Summary and Reports',
                'category': 'Analysis',
                'keywords': ['summary', 'report', 'daily', 'statistics', 'analysis'],
                'related_topics': ['export_data', 'work_tracking', 'break_management'],
                'content': '''
# Daily Summary and Reports

The daily summary provides comprehensive insights into your work patterns, productivity, and time management.

## Accessing Daily Summary

### View Current Day
- Click "Show Summary" button in main window
- Or use keyboard shortcut (Ctrl+Shift+D)
- Summary window opens with today's data

### Navigate Between Days
- Use date picker to select different days
- Browse forward/backward with navigation buttons
- Jump to specific weeks or months

## Summary Components

### Work Time Analysis
- **Total Work Time**: Sum of all work sessions
- **Goal Progress**: Percentage of daily target completed
- **Session Count**: Number of separate work periods
- **Average Session**: Mean duration of work sessions
- **Longest Session**: Duration of longest continuous work period

### Break Analysis
- **Total Break Time**: Sum of all break periods
- **Break Count**: Number of breaks taken
- **Average Break**: Mean break duration
- **Longest Break**: Duration of longest break
- **Break Frequency**: Breaks per hour of work

### Productivity Metrics
- **Efficiency Ratio**: Work time vs. total time
- **Work/Break Balance**: Ratio of work to break time
- **Target Achievement**: Progress toward daily goals
- **Overtime Status**: Hours beyond standard work day

## Visual Reports

### Charts and Graphs
- **Time Distribution**: Pie chart of work vs. break time
- **Session Timeline**: Hourly breakdown of activities
- **Progress Indicators**: Visual goal completion status
- **Trend Analysis**: Comparison with previous days

### Color Coding
- **Green**: On track or ahead of schedule
- **Yellow**: Slightly behind or approaching limits
- **Red**: Significantly behind or over limits
- **Blue**: Break periods and non-work time

## Historical Data

### Weekly Views
- Aggregate data for the current week
- Day-by-day comparison charts
- Weekly totals and averages
- Progress toward weekly goals

### Monthly Analysis
- Monthly work hour totals
- Average daily performance
- Best and worst performing days
- Monthly productivity trends

## Exporting Summary Data

### Quick Export Options
- Print current summary
- Save as PDF report
- Export to spreadsheet (CSV)
- Share via email (if configured)

### Detailed Reports
Access via File > Export for:
- Custom date range reports
- Detailed session breakdowns
- Comparative analysis reports
- Professional formatting options

## Using Summary Data

### Performance Optimization
1. **Identify Patterns**: Look for consistent productive times
2. **Optimize Breaks**: Adjust break timing and duration
3. **Set Realistic Goals**: Use historical data to set targets
4. **Track Improvements**: Monitor progress over time

### Problem Identification
- **Frequent Short Sessions**: May indicate interruptions
- **Long Breaks**: Could suggest scheduling issues
- **Inconsistent Patterns**: May need routine adjustments
- **Goal Misalignment**: Targets may need modification

Related Topics: [Export Data](export_data), [Work Tracking](work_tracking), [Settings Configuration](settings)
'''
            },
            {
                'id': 'export_data',
                'title': 'Exporting and Backup',
                'category': 'Data Management',
                'keywords': ['export', 'backup', 'save', 'csv', 'pdf', 'json'],
                'related_topics': ['daily_summary', 'settings', 'backup_restore'],
                'content': '''
# Exporting and Backup

Worklog Manager provides comprehensive data export and backup options to keep your work data safe and accessible.

## Export Formats

### CSV (Comma-Separated Values)
- **Best for**: Spreadsheet analysis, data processing
- **Contains**: All session data with timestamps
- **Compatible with**: Excel, Google Sheets, LibreOffice Calc
- **Use cases**: Detailed analysis, payroll reporting, time billing

### JSON (JavaScript Object Notation)
- **Best for**: Technical users, data integration
- **Contains**: Complete structured data including metadata
- **Compatible with**: Programming tools, databases
- **Use cases**: Data migration, custom analysis, API integration

### PDF (Portable Document Format)
- **Best for**: Professional reports, archiving
- **Contains**: Formatted reports with charts and summaries
- **Compatible with**: All PDF readers
- **Use cases**: Client reports, HR documentation, presentations

## Export Options

### Quick Export
Access via main menu File > Export:
1. **Current Day**: Export today's data only
2. **Current Week**: Export this week's sessions
3. **Current Month**: Export this month's data
4. **All Data**: Export complete database

### Custom Export
Choose File > Export > Custom Range:
- **Date Range Selection**: Pick specific start and end dates
- **Format Selection**: Choose CSV, JSON, or PDF
- **Detail Level**: Summary only or complete session data
- **Filter Options**: Include/exclude breaks, specific session types

## Automatic Backup

### Backup Settings
Configure in Settings > Backup:
- **Auto Backup**: Enable automatic daily/weekly backups
- **Backup Location**: Choose where backups are stored
- **Retention Policy**: How long to keep old backups
- **Backup Format**: Compressed or uncompressed

### Backup Schedule
- **Daily**: Backup created every night at specified time
- **Weekly**: Backup created on chosen day of week
- **On Exit**: Backup created when closing application
- **Manual**: Create backup anytime via Settings

### Backup Contents
Automatic backups include:
- Complete work session database
- Application settings and preferences
- Custom themes and configurations
- Export templates and formats

## Data Recovery

### Restoring from Backup
If you need to restore data:
1. Go to Settings > Backup
2. Click "Restore from Backup"
3. Select backup file to restore
4. Choose what to restore (data, settings, or both)
5. Confirm restoration

### Import Data
To import data from another source:
1. File > Import Data
2. Select file format (CSV, JSON)
3. Map data fields if needed
4. Preview imported data
5. Confirm import

## Professional Reporting

### PDF Report Features
Professional PDF exports include:
- **Executive Summary**: Key metrics and highlights
- **Detailed Breakdown**: Session-by-session analysis
- **Charts and Graphs**: Visual representation of data
- **Comparative Analysis**: Period-over-period comparisons
- **Custom Branding**: Add company logo and formatting

### Report Customization
Customize reports via Settings > Export:
- **Report Template**: Choose from predefined layouts
- **Color Scheme**: Match company or personal branding
- **Data Fields**: Select which information to include
- **Chart Types**: Customize visual elements

## Data Security and Privacy

### Local Storage
- All data stored locally on your computer
- No cloud storage unless you choose to backup externally
- Full control over your data

### Backup Security
- Backups can be encrypted (optional)
- Store backups on secure external drives
- Regular backup verification

### Export Privacy
- Remove sensitive information before sharing
- Anonymize data for external reporting
- Control what information is included

## Integration Options

### Payroll Systems
- Export data in formats compatible with common payroll software
- Include necessary fields for time tracking
- Maintain audit trails

### Project Management
- Export session data for project time tracking
- Include project codes and categories
- Generate client billing reports

Related Topics: [Daily Summary](daily_summary), [Settings Configuration](settings), [Backup and Restore](backup_restore)
'''
            },
            {
                'id': 'keyboard_shortcuts',
                'title': 'Keyboard Shortcuts',
                'category': 'Productivity',
                'keywords': ['keyboard', 'shortcuts', 'hotkeys', 'quick', 'keys'],
                'related_topics': ['settings', 'productivity_tips'],
                'content': '''
# Keyboard Shortcuts

Keyboard shortcuts allow you to quickly access common functions without using the mouse, significantly improving your productivity.

## Default Shortcuts

### Work Session Control
- **Ctrl+Shift+S**: Start Work Session
- **Ctrl+Shift+E**: End Work Session
- **Ctrl+Shift+B**: Take Break
- **Ctrl+Shift+R**: End Break (Resume Work)

### Information and Reports
- **Ctrl+Shift+D**: Show Daily Summary
- **Ctrl+Shift+X**: Export Data
- **Ctrl+Shift+H**: Show this Help System

### Application Control
- **Ctrl+Comma**: Open Settings
- **Ctrl+Q**: Quit Application
- **F1**: Show Help
- **Escape**: Close Current Dialog

## Customizing Shortcuts

### Access Shortcut Settings
1. Open Settings (Ctrl+Comma)
2. Navigate to "Shortcuts" tab
3. Click on the shortcut field you want to change
4. Click "Record" button
5. Press the desired key combination
6. Click "Accept" to save

### Shortcut Guidelines
**Valid Modifiers**:
- Ctrl (Control key)
- Alt (Alt key)
- Shift (Shift key)
- Win (Windows key - use sparingly)

**Valid Keys**:
- Letters (A-Z)
- Numbers (0-9)
- Function keys (F1-F12)
- Special keys (Space, Enter, Escape, etc.)

**Best Practices**:
- Use Ctrl+Shift for application-specific shortcuts
- Avoid system shortcuts (like Ctrl+C, Ctrl+V)
- Keep shortcuts memorable and logical
- Use function keys for secondary functions

## Quick Action Tips

### Rapid Time Tracking
For fastest time tracking:
1. **Ctrl+Shift+S** when you start working
2. **Ctrl+Shift+B** when taking breaks
3. **Ctrl+Shift+R** when returning from break
4. **Ctrl+Shift+E** when ending work

### Efficient Workflow
Typical daily workflow using shortcuts:
1. Start application
2. **Ctrl+Shift+S** to begin work
3. Work for 1-2 hours
4. **Ctrl+Shift+B** for break
5. **Ctrl+Shift+R** after break
6. Repeat work/break cycle
7. **Ctrl+Shift+E** to end day
8. **Ctrl+Shift+D** to review summary

## System Tray Shortcuts

When minimized to system tray:
- **Double-click tray icon**: Restore window
- **Right-click tray icon**: Access context menu
- **Global shortcuts still work**: Even when minimized

## Accessibility Features

### Alternative Input Methods
- All shortcuts work with accessibility software
- Voice recognition software can trigger shortcuts
- Screen readers announce shortcut availability

### Visual Indicators
- Shortcut keys shown in menus
- Tooltip help shows shortcuts
- Status bar displays active shortcuts

## Troubleshooting Shortcuts

### Shortcuts Not Working
1. **Check for conflicts**: Ensure no other software uses same combination
2. **Verify settings**: Go to Settings > Shortcuts to confirm
3. **Restart application**: Some changes require restart
4. **Check focus**: Ensure main window has focus

### Conflicting Applications
If shortcuts conflict with other software:
1. Choose different key combinations
2. Disable conflicting software shortcuts
3. Use application-specific shortcuts only
4. Contact support if issues persist

## Advanced Shortcut Features

### Context-Sensitive Shortcuts
- Some shortcuts only work in specific contexts
- Dialog boxes have their own shortcut sets
- Help system uses standard navigation shortcuts

### Shortcut Themes
Create shortcut "themes" for different work styles:
- **Minimal**: Just essential shortcuts
- **Power User**: All available shortcuts
- **Custom**: Personalized combinations

Related Topics: [Settings Configuration](settings), [Productivity Tips](productivity_tips), [System Tray](system_tray)
'''
            },
            {
                'id': 'settings',
                'title': 'Settings and Configuration',
                'category': 'Configuration',
                'keywords': ['settings', 'configuration', 'preferences', 'options'],
                'related_topics': ['themes', 'notifications', 'backup_restore'],
                'content': '''
# Settings and Configuration

Customize Worklog Manager to match your work style, preferences, and organizational requirements through comprehensive configuration options.

## Accessing Settings

### Opening Settings
- Click File > Settings in menu bar
- Use keyboard shortcut: Ctrl+Comma
- Click settings icon in toolbar (if available)
- Access via system tray context menu

### Settings Organization
Settings are organized into logical categories:
- **Work Norms**: Daily targets and work standards
- **Appearance**: Themes, fonts, and visual preferences
- **Notifications**: Alerts and reminder configuration
- **Backup**: Automatic backup and data protection
- **Shortcuts**: Keyboard shortcut customization
- **General**: Application behavior and integration

## Work Norms Configuration

### Daily Work Standards
- **Hours per day**: Set your standard work day length (default: 7.5 hours)
- **Minutes per day**: Automatically calculated from hours
- **Flexible targets**: Adjust based on your schedule

### Break Settings
- **Max break duration**: Longest allowed single break (default: 60 minutes)
- **Daily break limit**: Total break time allowed per day (default: 120 minutes)
- **Break warnings**: Alerts for approaching limits

### Overtime Management
- **Overtime threshold**: Hours that constitute overtime (default: 8 hours)
- **Warning threshold**: When to alert about approaching overtime
- **Overtime notifications**: Configure alerts and reminders

## Appearance Customization

### Theme Selection
Choose from built-in themes:
- **Light Theme**: Traditional light interface
- **Dark Theme**: Easy on eyes for long work sessions
- **High Contrast**: Enhanced accessibility
- **Custom Themes**: Create your own color schemes

### Font Configuration
- **Font family**: Choose from system fonts
- **Font size**: Adjust for comfort and readability
- **Font weight**: Normal, bold, or light options

### Window Behavior
- **Remember position**: Save window location between sessions
- **Remember size**: Maintain preferred window dimensions
- **Startup behavior**: How application opens

## Notification Settings

### General Notification Options
- **Enable notifications**: Turn all notifications on/off
- **System notifications**: Use operating system notification system
- **Sound alerts**: Audio notifications for important events

### Work Reminders
- **Start work reminder**: Daily prompt to begin work
- **Work start time**: When to send start reminder
- **End day reminder**: Prompt to finish work day
- **End day time**: When to send end reminder

### Break Notifications
- **Break reminders**: Periodic prompts to take breaks
- **Break interval**: How often to remind (default: 90 minutes)
- **Long break warnings**: Alerts for extended breaks
- **Return reminders**: Prompts to return from break

## Backup Configuration

### Automatic Backup
- **Enable auto backup**: Turn automatic backups on/off
- **Backup frequency**: Daily, weekly, or monthly
- **Backup time**: When to perform backups
- **Backup location**: Where to store backup files

### Backup Options
- **Compress backups**: Save space with ZIP compression
- **Backup on exit**: Create backup when closing app
- **Include exports**: Save export templates in backup
- **Include settings**: Backup configuration data

### Retention Management
- **Max backup files**: How many backups to keep
- **Retention days**: How long to keep old backups
- **Cleanup options**: Automatic old backup removal

## Advanced Settings

### System Integration
- **System tray**: Enable tray icon and minimization
- **Startup options**: Launch with system or manually
- **File associations**: Handle worklog files automatically

### Data Management
- **Database optimization**: Automatic database maintenance
- **Import/export defaults**: Preferred formats and options
- **Data validation**: Ensure data integrity

### Performance Options
- **Update frequency**: How often to refresh displays
- **Memory management**: Optimize for low-memory systems
- **Background processing**: Control background tasks

## Importing and Exporting Settings

### Settings Export
Save your configuration:
1. Go to Settings > General
2. Click "Export Settings"
3. Choose location and filename
4. Settings saved as JSON file

### Settings Import
Restore or share configuration:
1. Go to Settings > General
2. Click "Import Settings"
3. Select previously exported settings file
4. Choose which settings to import
5. Restart application if required

### Sharing Configurations
- Export settings to share with team members
- Create standard configurations for organizations
- Backup settings before major changes

## Troubleshooting Settings

### Reset to Defaults
If settings become corrupted:
1. Click "Reset to Defaults" in any settings tab
2. Confirm you want to reset all settings
3. Application will restart with default configuration
4. Reconfigure as needed

### Settings Not Saving
If changes don't persist:
1. Check file permissions in settings directory
2. Ensure application has write access
3. Try running as administrator (Windows)
4. Check disk space availability

### Performance Issues
If application becomes slow after configuration changes:
1. Reset to default settings
2. Apply changes gradually
3. Disable resource-intensive features
4. Check system requirements

Related Topics: [Themes and Appearance](themes), [Notifications](notifications), [Backup and Restore](backup_restore)
'''
            },
            {
                'id': 'troubleshooting',
                'title': 'Troubleshooting and FAQ',
                'category': 'Support',
                'keywords': ['troubleshooting', 'problems', 'issues', 'faq', 'help'],
                'related_topics': ['settings', 'backup_restore'],
                'content': '''
# Troubleshooting and FAQ

Common issues, solutions, and frequently asked questions to help you get the most out of Worklog Manager.

## Common Issues

### Application Won't Start
**Problem**: Worklog Manager doesn't launch or crashes immediately

**Solutions**:
1. **Check system requirements**: Ensure your system meets minimum requirements
2. **Run as administrator**: Right-click and "Run as administrator" (Windows)
3. **Check file permissions**: Ensure you have read/write access to application folder
4. **Antivirus interference**: Add application to antivirus exceptions
5. **Reinstall application**: Download and reinstall latest version

### Data Not Saving
**Problem**: Work sessions or settings don't persist between application restarts

**Solutions**:
1. **Check disk space**: Ensure adequate free space on system drive
2. **File permissions**: Verify write access to data directory
3. **Database corruption**: Restore from backup or reset database
4. **Antivirus blocking**: Check if antivirus is blocking file writes
5. **Manual save**: Use File > Save to force data save

### Timer Accuracy Issues
**Problem**: Timer seems inaccurate or sessions show wrong durations

**Solutions**:
1. **System clock**: Verify system date and time are correct
2. **Time zones**: Check time zone settings, especially after travel
3. **Sleep mode**: Computer sleep can affect timing accuracy
4. **Manual correction**: Edit session times in daily summary if needed
5. **Restart sessions**: End and restart work session for accuracy

### Performance Problems
**Problem**: Application runs slowly or uses excessive resources

**Solutions**:
1. **Close unused applications**: Free up system memory
2. **Database optimization**: Use Settings > Advanced > Optimize Database
3. **Reduce visual effects**: Switch to light theme or disable animations
4. **Update software**: Ensure you're running the latest version
5. **System restart**: Restart computer to clear memory

## Frequently Asked Questions

### General Usage

**Q: How accurate is the time tracking?**
A: Time tracking is accurate to the second. The application uses system time and accounts for computer sleep/hibernate modes.

**Q: Can I edit recorded work sessions?**
A: Yes, you can edit session times through the daily summary view. Click on any session to modify start/end times.

**Q: What happens if I forget to start/stop the timer?**
A: You can manually add or edit sessions in the daily summary. Use the "Add Session" button to create missing entries.

**Q: Can multiple people use the same computer?**
A: Yes, each user account maintains separate data. Switch between user accounts on your computer for individual tracking.

### Data Management

**Q: Where is my data stored?**
A: Data is stored locally in your user profile directory. The exact location varies by operating system but is shown in Settings > General.

**Q: How do I backup my data?**
A: Enable automatic backups in Settings > Backup, or manually export data via File > Export. Regular backups are recommended.

**Q: Can I sync data between computers?**
A: Not automatically. Export data from one computer and import on another, or store backups in a shared cloud folder.

**Q: How long is data kept?**
A: Data is kept indefinitely unless you manually delete it. Use File > Archive Old Data to move old records to separate files.

### Features and Functionality

**Q: Can I track time for different projects?**
A: The basic version tracks total work time. Project-specific tracking can be managed through export categories and manual notation.

**Q: Does the app work offline?**
A: Yes, Worklog Manager works completely offline. No internet connection is required for time tracking or data management.

**Q: Can I customize the work day length?**
A: Yes, go to Settings > Work Norms to set custom daily hour targets, break limits, and overtime thresholds.

**Q: How do notifications work?**
A: Notifications remind you to start work, take breaks, and end your day. Configure timing and types in Settings > Notifications.

## Error Messages

### "Database Error"
- **Cause**: Database file corruption or access issues
- **Solution**: Restore from backup or reset database in Settings > Advanced

### "Permission Denied"
- **Cause**: Insufficient file system permissions
- **Solution**: Run as administrator or check folder permissions

### "Settings Could Not Be Saved"
- **Cause**: Settings file is read-only or disk is full
- **Solution**: Check disk space and file permissions in settings directory

### "Export Failed"
- **Cause**: Invalid export location or format issues
- **Solution**: Choose different location or format, ensure adequate disk space

## Getting Help

### Built-in Help
- **F1 Key**: Opens this help system
- **Context Help**: Hover over buttons and fields for tooltips
- **Status Messages**: Check status bar for helpful information

### Online Resources
- **User Manual**: Complete documentation available online
- **Video Tutorials**: Step-by-step guides for common tasks
- **Community Forum**: User discussions and tips
- **Support Email**: Direct technical support contact

### Reporting Issues
When reporting problems, include:
1. **Version number**: Found in Help > About
2. **Operating system**: Windows version, Mac version, etc.
3. **Error messages**: Exact text of any error messages
4. **Steps to reproduce**: What you were doing when issue occurred
5. **Screenshots**: Visual information helps diagnose issues

### System Information
To get system information for support:
1. Go to Help > System Information
2. Copy the displayed information
3. Include in support requests

## Prevention and Best Practices

### Regular Maintenance
- **Weekly**: Review daily summaries for accuracy
- **Monthly**: Create manual backup and verify data
- **Quarterly**: Clean up old data and optimize database
- **Annually**: Update to latest software version

### Data Safety
- **Enable auto-backup**: Protect against data loss
- **Export regularly**: Create external copies of important data
- **Test restores**: Verify backups work before you need them
- **Monitor disk space**: Ensure adequate space for data and backups

Related Topics: [Settings Configuration](settings), [Backup and Restore](backup_restore), [Getting Started](getting_started)
'''
            }
        ]
        
        # Create help topics and organize by category
        for topic_data in topics_data:
            topic = HelpTopic(**topic_data)
            self.topics[topic.id] = topic
            
            # Add to category
            if topic.category not in self.categories:
                self.categories[topic.category] = []
            self.categories[topic.category].append(topic.id)
    
    def search_topics(self, query: str) -> List[HelpTopic]:
        """Search help topics by query string."""
        query_lower = query.lower()
        results = []
        
        for topic in self.topics.values():
            # Check title
            if query_lower in topic.title.lower():
                results.append(topic)
                continue
            
            # Check keywords
            if any(query_lower in keyword.lower() for keyword in topic.keywords):
                results.append(topic)
                continue
            
            # Check content
            if query_lower in topic.content.lower():
                results.append(topic)
        
        return results
    
    def get_topic(self, topic_id: str) -> Optional[HelpTopic]:
        """Get a specific help topic by ID."""
        return self.topics.get(topic_id)
    
    def get_category_topics(self, category: str) -> List[HelpTopic]:
        """Get all topics in a specific category."""
        topic_ids = self.categories.get(category, [])
        return [self.topics[tid] for tid in topic_ids if tid in self.topics]
    
    def get_related_topics(self, topic_id: str) -> List[HelpTopic]:
        """Get topics related to the specified topic."""
        topic = self.topics.get(topic_id)
        if not topic:
            return []
        
        related = []
        for related_id in topic.related_topics:
            if related_id in self.topics:
                related.append(self.topics[related_id])
        
        return related

class HelpDialog:
    """Main help dialog window with navigation and search."""
    
    def __init__(self, parent: tk.Widget, help_system: HelpSystem = None):
        self.parent = parent
        self.help_system = help_system or HelpSystem()
        
        self.dialog = None
        self.content_frame = None
        self.navigation_frame = None
        self.search_frame = None
        
        self.current_topic = None
        self.history = []
        self.history_index = -1
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the help dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Worklog Manager Help")
        self.dialog.geometry("900x700")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create main layout
        main_paned = ttk.PanedWindow(self.dialog, orient=tk.HORIZONTAL)
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Navigation
        self.create_navigation_panel(main_paned)
        
        # Right panel - Content
        self.create_content_panel(main_paned)
        
        # Load initial topic
        self.show_topic('getting_started')
    
    def create_navigation_panel(self, parent):
        """Create the navigation panel with categories and search."""
        nav_frame = ttk.Frame(parent)
        parent.add(nav_frame, weight=30)
        
        # Search section
        search_frame = ttk.LabelFrame(nav_frame, text="Search Help", padding=5)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill='x', pady=2)
        search_entry.bind('<Return>', self.perform_search)
        
        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(fill='x', pady=2)
        
        # Categories section
        categories_frame = ttk.LabelFrame(nav_frame, text="Categories", padding=5)
        categories_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Category tree
        self.category_tree = ttk.Treeview(categories_frame, show='tree')
        self.category_tree.pack(fill='both', expand=True)
        
        # Populate categories
        self.populate_categories()
        
        # Bind selection
        self.category_tree.bind('<<TreeviewSelect>>', self.on_category_select)
    
    def create_content_panel(self, parent):
        """Create the content panel with topic display."""
        content_frame = ttk.Frame(parent)
        parent.add(content_frame, weight=70)
        
        # Toolbar
        toolbar = ttk.Frame(content_frame)
        toolbar.pack(fill='x', padx=5, pady=2)
        
        # Navigation buttons
        self.back_btn = ttk.Button(toolbar, text="◀ Back", command=self.go_back, state='disabled')
        self.back_btn.pack(side='left', padx=2)
        
        self.forward_btn = ttk.Button(toolbar, text="Forward ▶", command=self.go_forward, state='disabled')
        self.forward_btn.pack(side='left', padx=2)
        
        # Home button
        ttk.Button(toolbar, text="🏠 Home", command=lambda: self.show_topic('getting_started')).pack(side='left', padx=10)
        
        # Print button
        ttk.Button(toolbar, text="🖨 Print", command=self.print_topic).pack(side='right', padx=2)
        
        # Content area with scrolling
        content_container = ttk.Frame(content_frame)
        content_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrolled text for content
        self.content_text = scrolledtext.ScrolledText(
            content_container, 
            wrap=tk.WORD, 
            padx=10, 
            pady=10,
            font=('Arial', 11)
        )
        self.content_text.pack(fill='both', expand=True)
        
        # Configure text tags for formatting
        self.setup_text_formatting()
    
    def setup_text_formatting(self):
        """Setup text formatting tags."""
        # Headers
        self.content_text.tag_config('h1', font=('Arial', 16, 'bold'), spacing3=10)
        self.content_text.tag_config('h2', font=('Arial', 14, 'bold'), spacing1=10, spacing3=5)
        self.content_text.tag_config('h3', font=('Arial', 12, 'bold'), spacing1=5, spacing3=3)
        
        # Body text
        self.content_text.tag_config('body', font=('Arial', 11))
        self.content_text.tag_config('code', font=('Courier', 10), background='#f0f0f0')
        
        # Links
        self.content_text.tag_config('link', foreground='blue', underline=True)
        self.content_text.tag_bind('link', '<Button-1>', self.on_link_click)
        self.content_text.tag_bind('link', '<Enter>', lambda e: self.content_text.configure(cursor='hand2'))
        self.content_text.tag_bind('link', '<Leave>', lambda e: self.content_text.configure(cursor=''))
        
        # Lists
        self.content_text.tag_config('bullet', lmargin1=20, lmargin2=30)
    
    def populate_categories(self):
        """Populate the category tree."""
        for category, topic_ids in self.help_system.categories.items():
            category_node = self.category_tree.insert('', 'end', text=category, values=[category])
            
            for topic_id in topic_ids:
                topic = self.help_system.get_topic(topic_id)
                if topic:
                    self.category_tree.insert(category_node, 'end', text=topic.title, values=[topic_id])
    
    def on_category_select(self, event):
        """Handle category/topic selection."""
        selection = self.category_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.category_tree.item(item, 'values')
        
        if values:
            topic_id = values[0]
            # Only show topic if it's not a category
            if topic_id in self.help_system.topics:
                self.show_topic(topic_id)
    
    def show_topic(self, topic_id: str):
        """Display a help topic."""
        topic = self.help_system.get_topic(topic_id)
        if not topic:
            return
        
        # Add to history
        if self.current_topic != topic_id:
            self.history = self.history[:self.history_index + 1]
            self.history.append(topic_id)
            self.history_index = len(self.history) - 1
            self.update_navigation_buttons()
        
        self.current_topic = topic_id
        
        # Clear content
        self.content_text.delete(1.0, tk.END)
        
        # Parse and display content
        self.parse_and_display_content(topic.content)
    
    def parse_and_display_content(self, content: str):
        """Parse markdown-like content and display with formatting."""
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.rstrip()
            
            if not line:
                self.content_text.insert(tk.END, '\n')
                continue
            
            # Headers
            if line.startswith('# '):
                self.content_text.insert(tk.END, line[2:] + '\n', 'h1')
            elif line.startswith('## '):
                self.content_text.insert(tk.END, line[3:] + '\n', 'h2')
            elif line.startswith('### '):
                self.content_text.insert(tk.END, line[4:] + '\n', 'h3')
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                self.content_text.insert(tk.END, '• ' + line[2:] + '\n', 'bullet')
            elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                # Numbered lists
                self.content_text.insert(tk.END, line.strip() + '\n', 'bullet')
            
            # Code blocks
            elif line.startswith('```'):
                continue  # Skip code block markers for now
            
            # Regular text with inline formatting
            else:
                self.parse_inline_formatting(line + '\n')
    
    def parse_inline_formatting(self, text: str):
        """Parse inline formatting like links and code."""
        # Simple link parsing [text](topic_id)
        import re
        
        pos = 0
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
            # Insert text before link
            if match.start() > pos:
                self.content_text.insert(tk.END, text[pos:match.start()], 'body')
            
            # Insert link
            link_text = match.group(1)
            link_target = match.group(2)
            
            start_pos = self.content_text.index(tk.END + '-1c')
            self.content_text.insert(tk.END, link_text, 'link')
            end_pos = self.content_text.index(tk.END + '-1c')
            
            # Store link target
            self.content_text.tag_add(f'link_{link_target}', start_pos, end_pos)
            
            pos = match.end()
        
        # Insert remaining text
        if pos < len(text):
            self.content_text.insert(tk.END, text[pos:], 'body')
    
    def on_link_click(self, event):
        """Handle link clicks."""
        # Get all tags at click position
        tags = self.content_text.tag_names(tk.CURRENT)
        
        for tag in tags:
            if tag.startswith('link_'):
                topic_id = tag[5:]  # Remove 'link_' prefix
                if topic_id in self.help_system.topics:
                    self.show_topic(topic_id)
                break
    
    def perform_search(self, event=None):
        """Perform search and show results."""
        query = self.search_var.get().strip()
        if not query:
            return
        
        results = self.help_system.search_topics(query)
        
        if not results:
            messagebox.showinfo("Search Results", f"No topics found matching '{query}'")
            return
        
        # Show search results
        self.show_search_results(query, results)
    
    def show_search_results(self, query: str, results: List[HelpTopic]):
        """Display search results."""
        self.content_text.delete(1.0, tk.END)
        
        self.content_text.insert(tk.END, f"Search Results for '{query}'\n", 'h1')
        self.content_text.insert(tk.END, f"Found {len(results)} topic(s)\n\n", 'body')
        
        for i, topic in enumerate(results, 1):
            # Topic title as link
            start_pos = self.content_text.index(tk.END)
            self.content_text.insert(tk.END, f"{i}. {topic.title}\n", 'link')
            end_pos = self.content_text.index(tk.END + '-1c')
            
            self.content_text.tag_add(f'link_{topic.id}', start_pos, end_pos)
            
            # Topic category and keywords
            self.content_text.insert(tk.END, f"   Category: {topic.category}\n", 'body')
            if topic.keywords:
                keywords_text = ', '.join(topic.keywords[:5])  # Show first 5 keywords
                self.content_text.insert(tk.END, f"   Keywords: {keywords_text}\n", 'body')
            
            self.content_text.insert(tk.END, '\n', 'body')
    
    def go_back(self):
        """Navigate back in history."""
        if self.history_index > 0:
            self.history_index -= 1
            topic_id = self.history[self.history_index]
            self.current_topic = topic_id
            
            topic = self.help_system.get_topic(topic_id)
            if topic:
                self.content_text.delete(1.0, tk.END)
                self.parse_and_display_content(topic.content)
            
            self.update_navigation_buttons()
    
    def go_forward(self):
        """Navigate forward in history."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            topic_id = self.history[self.history_index]
            self.current_topic = topic_id
            
            topic = self.help_system.get_topic(topic_id)
            if topic:
                self.content_text.delete(1.0, tk.END)
                self.parse_and_display_content(topic.content)
            
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Update navigation button states."""
        self.back_btn.config(state='normal' if self.history_index > 0 else 'disabled')
        self.forward_btn.config(state='normal' if self.history_index < len(self.history) - 1 else 'disabled')
    
    def print_topic(self):
        """Print current topic."""
        if not self.current_topic:
            return
        
        topic = self.help_system.get_topic(self.current_topic)
        if not topic:
            return
        
        # Create a simple text version for printing
        content = f"Worklog Manager Help: {topic.title}\n"
        content += "=" * (len(content) - 1) + "\n\n"
        content += topic.content
        
        # Open in default text editor for printing
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            os.startfile(temp_path)  # Windows
        except AttributeError:
            try:
                os.system(f'open "{temp_path}"')  # macOS
            except:
                os.system(f'xdg-open "{temp_path}"')  # Linux

class TooltipManager:
    """Manages tooltips for GUI elements."""
    
    def __init__(self):
        self.tooltips = {}
    
    def add_tooltip(self, widget: tk.Widget, text: str):
        """Add a tooltip to a widget."""
        self.tooltips[widget] = text
        
        def on_enter(event):
            self.show_tooltip(widget, text)
        
        def on_leave(event):
            self.hide_tooltip(widget)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def show_tooltip(self, widget: tk.Widget, text: str):
        """Show tooltip for widget."""
        try:
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='lightyellow', relief='solid', borderwidth=1)
            
            label = tk.Label(tooltip, text=text, background='lightyellow', 
                           font=('Arial', 9), wraplength=300, justify='left')
            label.pack()
            
            # Position tooltip
            x = widget.winfo_rootx() + widget.winfo_width() + 5
            y = widget.winfo_rooty() + widget.winfo_height() // 2
            
            tooltip.geometry(f"+{x}+{y}")
            
            # Store reference
            widget.tooltip_window = tooltip
            
            # Auto-hide after 5 seconds
            tooltip.after(5000, lambda: self.hide_tooltip(widget))
            
        except Exception as e:
            print(f"Error showing tooltip: {e}")
    
    def hide_tooltip(self, widget: tk.Widget):
        """Hide tooltip for widget."""
        try:
            if hasattr(widget, 'tooltip_window'):
                widget.tooltip_window.destroy()
                del widget.tooltip_window
        except Exception as e:
            pass