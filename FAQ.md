# Frequently Asked Questions (FAQ)

Common questions and answers about Worklog Manager.

## Table of Contents

- [General](#general)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Data & Privacy](#data--privacy)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## General

### What is Worklog Manager?
Worklog Manager is a professional desktop application for tracking work time with precision. It helps you monitor productive hours, manage breaks, calculate overtime, and generate comprehensive reports.

### Is it free?
Yes, Worklog Manager is open source and free to use under the MIT License.

### What platforms are supported?
Windows, macOS, and Linux are all supported. See [INSTALL.md](INSTALL.md) for platform-specific instructions.

### Do I need an internet connection?
No, Worklog Manager works entirely offline. All data is stored locally on your computer.

### Where is my data stored?
All data is stored locally in a SQLite database (`worklog.db`) in the application directory. No data is sent to external servers.

## Installation & Setup

### What are the system requirements?
- Python 3.7 or higher
- 256 MB RAM minimum (512 MB recommended)
- 50 MB disk space
- Any modern operating system

### Do I need to install any dependencies?
No, Worklog Manager uses only Python standard library modules. The optional PDF export feature requires the `reportlab` library.

### How do I install Python?
Download Python from [python.org](https://www.python.org/downloads/) and follow the installation instructions for your operating system.

### Can I run it without installing Python?
Currently, Python is required. Future releases may include standalone executables.

### How do I update to a new version?
1. Backup your data (`worklog.db`, `config.ini`, `settings.json`)
2. Download the new version
3. Replace old files with new ones
4. Copy back your data files
5. Run the application

## Usage

### How do I start tracking time?
1. Launch the application
2. Click "Start Day"
3. The timer begins automatically

### Can I track multiple work sessions per day?
Yes! Use Stop/Continue to pause and resume throughout the day. All sessions are combined into your daily total.

### What's the difference between Stop and End Day?
- **Stop**: Pause work temporarily (for breaks) - you can Continue later
- **End Day**: Complete tracking for the day - no more tracking until next day

### How do I record different break types?
Before clicking Stop, select the break type (Lunch, Coffee, or General) from the dropdown menu.

### Can I edit past entries?
Currently, direct editing is not supported. You can use the Revoke feature to undo recent actions or Reset Day to start over.

### What happens if I forget to stop the timer?
Use the Revoke feature to undo recent actions and correct the timing. You can revoke up to the last 5 actions.

### How do I see my overtime?
The Time Summary panel shows your overtime in real-time once you exceed your work norm (default: 7.5 hours).

## Data & Privacy

### Is my data private?
Yes, completely. All data is stored locally on your computer. No data is transmitted anywhere.

### Can I export my data?
Yes! Export to CSV, JSON, or PDF formats. Click "Export Data" and choose your preferred format.

### How do I backup my data?
Worklog Manager creates automatic backups in the `backups/` directory. You can also manually copy the `worklog.db` file.

### Can I delete my data?
Yes. Use "Reset Day" to clear today's data, or delete the `worklog.db` file to remove all data.

### Where are the log files?
Log files are stored in the `logs/` directory with daily file names like `worklog_YYYYMMDD.log`.

### Can I import data from another time tracking tool?
This feature is not currently available but may be added in future versions.

## Features

### What is the work norm?
The work norm is your target daily work hours (default: 7.5 hours). You can customize this in `config.ini`.

### How does overtime calculation work?
Overtime is any productive work time exceeding your configured work norm. It's calculated automatically and displayed in red.

### What is the Revoke feature?
Revoke lets you undo up to your last 5 actions (Start, Stop, Continue, End Day). It restores the application state to before that action.

### What does Reset Day do?
Reset Day completely clears all of today's data and returns the application to "Not Started" state. ⚠️ This cannot be undone!

### Can I customize keyboard shortcuts?
Yes, keyboard shortcuts can be customized in the Settings dialog.

### Does it support multiple users?
Each installation tracks one user. For multiple users, set up separate installations or use different user accounts on your computer.

### Can I run it on a network drive?
While possible, we recommend local installation for best performance. The SQLite database may have locking issues on network drives.

## Troubleshooting

### The application won't start
1. Verify Python 3.7+ is installed: `python --version`
2. Check that tkinter is available: `python -c "import tkinter"`
3. Review the log files for error messages
4. Ensure you have file permissions in the application directory

### I see "database is locked" error
1. Close all instances of the application
2. Check if another process is using the database
3. Restart your computer if the issue persists

### The timer is not updating
1. Restart the application
2. Check your system clock is correct
3. Verify the application is in "Working" state

### My data disappeared
1. Check the `backups/` directory for recent backups
2. Look for `worklog.db` in the application directory
3. Review log files for any errors
4. Restore from a backup if available

### Colors are not showing correctly
1. Try switching themes (Light/Dark) in Settings
2. Check your display settings
3. Update to the latest version

### Notifications are not appearing
1. Check notification settings in the Settings dialog
2. Verify your system allows notifications from Python applications
3. Try restarting the application

### Export is not working
1. Check you have write permissions to the `exports/` directory
2. For PDF export, ensure reportlab is installed: `pip install reportlab`
3. Review log files for specific error messages

## Development

### How can I contribute?
See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Can I suggest a feature?
Yes! Open a [feature request](https://github.com/your-username/worklog-manager/issues/new?template=feature_request.md) on GitHub.

### How do I report a bug?
Open a [bug report](https://github.com/your-username/worklog-manager/issues/new?template=bug_report.md) with details about the issue.

### Is the code well-documented?
Yes, the codebase follows PEP 8 standards and includes docstrings for all major functions and classes.

### Can I fork this project?
Yes! The MIT License allows you to fork, modify, and distribute the code. See [LICENSE](LICENSE) for details.

### How do I run tests?
```bash
pytest tests/
```

### Where can I find the API documentation?
Technical documentation is available in the `docs/` directory. See [TECHNICAL_SPECIFICATION.md](docs/TECHNICAL_SPECIFICATION.md).

## Still Have Questions?

If your question isn't answered here:

1. Check the [Documentation](docs/)
2. Search [existing issues](https://github.com/your-username/worklog-manager/issues)
3. Open a [new discussion](https://github.com/your-username/worklog-manager/discussions)
4. Create an [issue](https://github.com/your-username/worklog-manager/issues/new)

---

**Help improve this FAQ!** If you had a question that's not listed here, please submit a pull request to add it.

*Last updated: October 21, 2025*
