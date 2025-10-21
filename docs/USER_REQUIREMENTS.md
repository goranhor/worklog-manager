# Worklog Manager - User Requirements Document

## Executive Summary
This document outlines the requirements for a Python-based GUI application designed to track daily work hours for company employees. The system will ensure compliance with a 7.5-hour work day norm while providing detailed logging, break management, and comprehensive reporting capabilities.

## Functional Requirements

### FR1: Day Management
- **FR1.1**: Start Day button to begin worklog for current date
- **FR1.2**: End Day button to complete daily logging
- **FR1.3**: System prevents multiple active days
- **FR1.4**: Automatic date detection and display
- **FR1.5**: Validation to prevent starting day if already started

### FR2: Work Session Control
- **FR2.1**: Stop button to pause work when leaving workplace
- **FR2.2**: Continue button to resume work when returning
- **FR2.3**: Real-time timer display showing current session duration
- **FR2.4**: Visual indication of current work status (working/stopped)
- **FR2.5**: Seamless transition between work and pause states

### FR3: Break Management
- **FR3.1**: Support for multiple break types:
  - **FR3.1.1**: Lunch break
  - **FR3.1.2**: Coffee break
  - **FR3.1.3**: General break/interruption
- **FR3.2**: Break type selection before stopping work
- **FR3.3**: Automatic break time calculation and tracking
- **FR3.4**: Visual distinction between break types in logs

### FR4: Time Calculations
- **FR4.1**: Work norm compliance (7.5 hours = 450 minutes)
- **FR4.2**: Real-time calculation of:
  - **FR4.2.1**: Total work time
  - **FR4.2.2**: Total break time
  - **FR4.2.3**: Productive time (work minus breaks)
  - **FR4.2.4**: Remaining time to reach norm
  - **FR4.2.5**: Overtime (time exceeding norm)
- **FR4.3**: Visual indicators for time status (normal/overtime)
- **FR4.4**: Automatic updates every second

### FR5: Revoke/Undo System
- **FR5.1**: Revoke Start Day action
- **FR5.2**: Revoke End Day action
- **FR5.3**: Revoke Stop actions
- **FR5.4**: Revoke Continue actions
- **FR5.5**: Action history tracking for all operations
- **FR5.6**: Confirmation dialogs before revoke operations
- **FR5.7**: State restoration after revoke

### FR6: Data Persistence
- **FR6.1**: SQLite database for reliable data storage
- **FR6.2**: Daily log files in format: day.month.year
- **FR6.3**: Automatic saving of all actions and state changes
- **FR6.4**: Data backup and recovery capabilities
- **FR6.5**: Data integrity validation

### FR7: Export and Reporting
- **FR7.1**: Export data to multiple formats:
  - **FR7.1.1**: CSV for spreadsheet analysis
  - **FR7.1.2**: JSON for data processing
  - **FR7.1.3**: PDF for human-readable reports
- **FR7.2**: Date range selection for exports
- **FR7.3**: Daily, weekly, and monthly summary reports
- **FR7.4**: Export with detailed breakdown of:
  - Work sessions
  - Break periods
  - Time calculations
  - Action history

### FR8: User Interface
- **FR8.1**: Intuitive GUI with clear button layout
- **FR8.2**: Real-time status display
- **FR8.3**: Color-coded time indicators
- **FR8.4**: Confirmation dialogs for critical actions
- **FR8.5**: Error messages and user feedback
- **FR8.6**: Responsive design for different screen sizes

## Non-Functional Requirements

### NFR1: Performance
- **NFR1.1**: Application startup time < 3 seconds
- **NFR1.2**: Button response time < 1 second
- **NFR1.3**: Timer updates with 1-second precision
- **NFR1.4**: Database operations < 500ms
- **NFR1.5**: Export operations < 10 seconds for 1 year of data

### NFR2: Reliability
- **NFR2.1**: 99.9% uptime during work hours
- **NFR2.2**: Automatic recovery from unexpected shutdowns
- **NFR2.3**: Data loss prevention through frequent saves
- **NFR2.4**: Graceful error handling with user notifications
- **NFR2.5**: State persistence across application restarts

### NFR3: Usability
- **NFR3.1**: Minimal learning curve (< 5 minutes for basic operations)
- **NFR3.2**: Clear visual feedback for all actions
- **NFR3.3**: Intuitive button placement and labeling
- **NFR3.4**: Consistent user interface design
- **NFR3.5**: Accessibility features (keyboard shortcuts, clear fonts)

### NFR4: Maintainability
- **NFR4.1**: Modular code architecture
- **NFR4.2**: Comprehensive logging for debugging
- **NFR4.3**: Configuration file for customization
- **NFR4.4**: Clear documentation and code comments
- **NFR4.5**: Unit test coverage > 80%

### NFR5: Security
- **NFR5.1**: Local data storage (no cloud dependencies)
- **NFR5.2**: File access protection
- **NFR5.3**: Input validation for all user inputs
- **NFR5.4**: Secure backup file handling
- **NFR5.5**: No sensitive data exposure in logs

## User Scenarios

### Scenario 1: Normal Work Day
1. User arrives at office and clicks "Start Day"
2. Works for 3 hours, then clicks "Stop" with "Lunch" break type
3. After 30-minute lunch, clicks "Continue"
4. Works for 2 hours, clicks "Stop" with "Coffee" break type
5. After 15-minute coffee break, clicks "Continue"
6. Works for remaining 2.75 hours to complete 7.5-hour norm
7. Clicks "End Day" to finish logging

### Scenario 2: Overtime Work Day
1. User follows normal work day pattern
2. Continues working beyond 7.5 hours
3. System shows overtime accumulation in red
4. User ends day with 1.5 hours of overtime
5. System records and calculates overtime correctly

### Scenario 3: Interrupted Work Day
1. User starts day normally
2. Has multiple small interruptions (calls, meetings)
3. Uses "Stop" with "General" break type for each
4. System tracks all interruptions separately
5. Calculates total productive time accurately

### Scenario 4: Accidental Action Recovery
1. User accidentally clicks "End Day" too early
2. Uses "Revoke End Day" to continue working
3. Works additional time to reach norm
4. Properly ends day when complete
5. System maintains accurate time records

### Scenario 5: Data Export for Review
1. User wants to review last month's work patterns
2. Clicks "Export Data" and selects date range
3. Chooses CSV format for analysis
4. Reviews exported data in spreadsheet
5. Identifies patterns and improvement opportunities

## Acceptance Criteria

### AC1: Time Accuracy
- ✅ All time calculations accurate to the second
- ✅ Proper handling of daylight saving time changes
- ✅ Correct overtime calculations
- ✅ Accurate break time tracking

### AC2: Data Integrity
- ✅ No data loss during normal operations
- ✅ Successful recovery from application crashes
- ✅ Accurate state restoration after revoke operations
- ✅ Consistent data across database and log files

### AC3: User Experience
- ✅ Intuitive operation without training
- ✅ Clear visual feedback for all actions
- ✅ Fast response times for all operations
- ✅ Helpful error messages and recovery options

### AC4: Compliance
- ✅ Accurate tracking of 7.5-hour work norm
- ✅ Proper categorization of work vs. break time
- ✅ Detailed audit trail for all actions
- ✅ Exportable reports for management review

### AC5: Reliability
- ✅ Stable operation throughout work day
- ✅ Automatic saving prevents data loss
- ✅ Graceful handling of edge cases
- ✅ Consistent behavior across different scenarios

## Constraints and Assumptions

### Constraints
- **C1**: Python-based application with Tkinter GUI
- **C2**: SQLite database for local storage
- **C3**: Single-user application (no multi-user support)
- **C4**: Windows operating system compatibility
- **C5**: No internet connectivity required

### Assumptions
- **A1**: User works on single computer throughout day
- **A2**: System clock is accurate and stable
- **A3**: User has basic computer literacy
- **A4**: Work norm is consistent at 7.5 hours daily
- **A5**: Break types are sufficient for user needs

## Future Enhancements (Out of Scope)
- Multi-user support with user authentication
- Cloud synchronization and backup
- Mobile application companion
- Integration with company HR systems
- Advanced analytics and productivity insights
- Team management and reporting features
- Calendar integration for meeting tracking
- Automatic break detection using system monitoring

This requirements document ensures that all your needs are captured and will guide the implementation to deliver exactly what you need for effective work time tracking.