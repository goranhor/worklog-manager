# Changelog

All notable changes to Worklog Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-10-21

### Added
- Appearance settings now include window dimensions and maximized state options
- General behavior toggles (start minimized, confirm exit, minimize to tray) are applied throughout the app

### Changed
- System tray actions delegate to the main window to preserve geometry and maximize state when toggling visibility
- Window restoration logic now consistently lifts, focuses, and reapplies saved size when returning from the tray

### Fixed
- Eliminated shutdown errors by adding a cleanup helper for the system tray manager
- Prevented geometry loss when hiding and restoring the window via the system tray

## [1.4.0] - 2025-10-21

### Added
- Settings management system with persistent configuration
- Light/Dark theme support with custom color schemes
- Notification system for work reminders, break alerts, and overtime warnings
- Automated backup system with configurable retention policies
- Customizable keyboard shortcuts for all major functions
- System tray integration with quick actions
- Built-in help system and contextual documentation
- Cross-platform support enhancements (Windows, macOS, Linux)
- Monthly and yearly report generation
- Visual productivity charts and graphs

### Improved
- UI polish and professional styling
- Performance optimizations for large datasets
- Enhanced error handling and user feedback

## [1.3.0] - 2025-10-20

### Added
- CSV export functionality with spreadsheet-compatible format
- JSON export with complete metadata and analytics
- PDF export for professional formatted reports
- Daily summary reports with productivity metrics
- Break analysis and pattern tracking
- Date range export support (today, this week, custom ranges)
- Quick export options for common scenarios
- Automatic file naming and organized export directory
- Statistical trends and insights in exports

### Improved
- Export dialog with format selection
- Data aggregation for reporting
- File management for exports

## [1.2.0] - 2025-10-19

### Added
- Action history tracking with complete audit trail
- Revoke system to undo up to 5 recent actions
- Visual confirmation dialog for revoke operations
- Full state restoration when revoking actions
- Enhanced break tracking with visual indicators
- Reset Day functionality with double confirmation
- Real-time input validation with error messages
- Break history display with emoji status

### Improved
- State validation to prevent invalid transitions
- User feedback for all operations
- Safety mechanisms for data integrity

## [1.1.0] - 2025-10-18

### Added
- Real-time timer display with 1-second precision
- Break management system (Lunch, Coffee, General)
- Automatic overtime calculation
- Color-coded status indicators
- Time remaining countdown
- Session tracking and calculations

### Improved
- UI responsiveness and updates
- Time calculation accuracy
- Break type selection interface

## [1.0.0] - 2025-10-17

### Added
- Initial release
- Core time tracking functionality (Start Day, Stop, Continue, End Day)
- SQLite database for data storage
- Basic GUI with essential controls
- 7.5-hour work norm compliance tracking
- Productive time calculation
- Daily log files
- Action logging system
- Work session and break period tracking

### Features
- Start/Stop/Continue/End Day workflow
- Break period tracking
- Time summary display
- Database persistence
- Basic configuration system

---

## Release Notes

### Version 1.5.0 - Window & Tray Enhancements
Refined the desktop experience with configurable window sizing, more reliable tray behavior, and cleaner shutdowns. Settings from the general tab now take effect throughout the app, delivering a smoother daily workflow.

### Version 1.4.0 - Advanced Features Complete
This release completes Phase 4 of development, adding comprehensive settings management, themes, notifications, and system tray integration. The application now includes all planned features and is production-ready for professional use.

### Version 1.3.0 - Export & Reporting
Comprehensive export system with multiple format support (CSV, JSON, PDF) and detailed analytics. Users can now generate professional reports with productivity insights.

### Version 1.2.0 - Revoke & Reset
Enhanced user control with the ability to undo recent actions and reset the day when needed. Includes comprehensive validation and safety mechanisms.

### Version 1.1.0 - Enhanced Tracking
Improved time tracking accuracy and user experience with real-time updates and better visual feedback.

### Version 1.0.0 - Foundation
Solid foundation with core time tracking, database persistence, and essential workflow features.
