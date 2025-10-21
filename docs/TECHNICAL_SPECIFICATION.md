# Worklog Manager - Technical Specification

## Application Flow Diagram

### State Machine
```
┌─────────────────┐
│   NOT_STARTED   │ ──── Start Day ───► ┌─────────────────┐
└─────────────────┘                      │     WORKING     │
         ▲                               └─────────────────┘
         │                                        │
         │ Revoke Start                          │ Stop (Break)
         │                                        ▼
┌─────────────────┐                      ┌─────────────────┐
│   DAY_ENDED     │ ◄──── End Day ────── │   ON_BREAK      │
└─────────────────┘                      └─────────────────┘
         │                                        │
         │ Revoke End                            │ Continue
         │                                        ▼
         └─────────────────────────────────────► WORKING
```

## Detailed Component Specifications

### 1. Main Application Window (`gui/main_window.py`)

#### Window Properties
- **Size**: 700x500 pixels (resizable)
- **Title**: "Worklog Manager v1.5.0"
- **Icon**: Custom work timer icon
- **Position**: Center screen on startup

#### Layout Structure
```python
class MainWindow:
    def __init__(self):
        # Header section
        self.date_label = ttk.Label()      # Current date display
        self.status_label = ttk.Label()    # Current status
        
        # Control buttons section
        self.start_day_btn = ttk.Button()
        self.end_day_btn = ttk.Button()
        self.stop_btn = ttk.Button()
        self.continue_btn = ttk.Button()
        
        # Break selection section
        self.break_type_var = tk.StringVar()
        self.lunch_radio = ttk.Radiobutton()
        self.coffee_radio = ttk.Radiobutton()
        self.general_radio = ttk.Radiobutton()
        
        # Time display section
        self.timer_frame = TimerDisplay()
        
        # Action buttons section
        self.export_btn = ttk.Button()
        self.revoke_btn = ttk.Button()
        self.settings_btn = ttk.Button()
```

### 2. Timer Display Component (`gui/components/timer_display.py`)

#### Real-time Updates
- **Update Frequency**: Every second
- **Display Format**: HH:MM:SS
- **Color Coding**: 
  - Green: Within norm (< 7.5 hours)
  - Orange: Approaching norm (7-7.5 hours)
  - Red: Overtime (> 7.5 hours)

#### Metrics Displayed
```python
class TimerDisplay:
    def __init__(self):
        self.current_session_time = "00:00:00"
        self.total_work_time = "00:00:00"
        self.break_time = "00:00:00"
        self.productive_time = "00:00:00"
        self.remaining_time = "07:30:00"
        self.overtime = "00:00:00"
        
    def update_display(self):
        # Updates every second via threading
        pass
```

### 3. Core Worklog Manager (`core/worklog_manager.py`)

#### Main Class Structure
```python
class WorklogManager:
    def __init__(self):
        self.db = Database()
        self.current_session = None
        self.timer_thread = None
        self.state = WorklogState.NOT_STARTED
        self.action_history = ActionHistory()
        
    def start_day(self) -> bool:
        """Start a new work day session"""
        
    def end_day(self) -> bool:
        """End the current work day"""
        
    def start_break(self, break_type: BreakType) -> bool:
        """Start a break period"""
        
    def end_break(self) -> bool:
        """End current break and resume work"""
        
    def revoke_last_action(self) -> bool:
        """Revoke the most recent action"""
```

#### State Validation
```python
def validate_action(self, action: ActionType) -> bool:
    """Validate if action is allowed in current state"""
    valid_transitions = {
        WorklogState.NOT_STARTED: [ActionType.START_DAY],
        WorklogState.WORKING: [ActionType.STOP, ActionType.END_DAY],
        WorklogState.ON_BREAK: [ActionType.CONTINUE],
        WorklogState.DAY_ENDED: [ActionType.REVOKE_END]
    }
    return action in valid_transitions.get(self.state, [])
```

### 4. Database Operations (`data/database.py`)

#### Connection Management
```python
class Database:
    def __init__(self, db_path: str = "worklog.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Establish database connection with error handling"""
        
    def create_tables(self):
        """Create all required tables if they don't exist"""
        
    def backup_database(self, backup_path: str):
        """Create database backup"""
```

#### Session Operations
```python
def create_session(self, date: str) -> int:
    """Create new work session for given date"""
    
def update_session(self, session_id: int, **kwargs):
    """Update session with new data"""
    
def get_session_by_date(self, date: str) -> dict:
    """Retrieve session data for specific date"""
    
def log_action(self, session_id: int, action_type: str, 
               timestamp: str, **kwargs):
    """Log user action to database"""
```

### 5. Time Calculator (`core/time_calculator.py`)

#### Core Calculations
```python
class TimeCalculator:
    WORK_NORM_MINUTES = 450  # 7.5 hours
    
    @staticmethod
    def calculate_work_time(actions: List[dict]) -> int:
        """Calculate total work time from action log"""
        
    @staticmethod
    def calculate_break_time(break_periods: List[dict]) -> int:
        """Calculate total break time"""
        
    @staticmethod
    def calculate_productive_time(work_time: int, break_time: int) -> int:
        """Calculate productive work time (work - breaks)"""
        
    @staticmethod
    def calculate_overtime(productive_time: int) -> int:
        """Calculate overtime minutes"""
        
    @staticmethod
    def calculate_remaining_time(productive_time: int) -> int:
        """Calculate remaining time to reach norm"""
```

### 6. Action History & Revoke System (`core/action_history.py`)

#### History Management
```python
class ActionHistory:
    def __init__(self):
        self.actions = []
        self.max_history = 50
        
    def add_action(self, action: Action):
        """Add action to history"""
        
    def get_last_action(self) -> Action:
        """Get most recent action"""
        
    def revoke_action(self, action_id: int) -> bool:
        """Revoke specific action and restore state"""
        
    def get_revokable_actions(self) -> List[Action]:
        """Get list of actions that can be revoked"""
```

#### Action Types
```python
class Action:
    def __init__(self, action_type: ActionType, timestamp: datetime,
                 state_before: WorklogState, state_after: WorklogState,
                 data: dict = None):
        self.id = uuid.uuid4()
        self.action_type = action_type
        self.timestamp = timestamp
        self.state_before = state_before
        self.state_after = state_after
        self.data = data or {}
        self.revoked = False
```

### 7. Export Manager (`data/export_manager.py`)

#### Export Formats
```python
class ExportManager:
    def export_to_csv(self, start_date: str, end_date: str, 
                     file_path: str) -> bool:
        """Export data to CSV format"""
        
    def export_to_json(self, start_date: str, end_date: str,
                      file_path: str) -> bool:
        """Export data to JSON format"""
        
    def generate_daily_report(self, date: str) -> str:
        """Generate daily summary report"""
        
    def generate_weekly_report(self, week_start: str) -> str:
        """Generate weekly summary report"""
```

#### Export Data Structure
```python
# CSV Export Columns
columns = [
    'Date', 'Start Time', 'End Time', 'Total Work Time',
    'Break Time', 'Productive Time', 'Overtime', 'Status',
    'Lunch Breaks', 'Coffee Breaks', 'General Breaks'
]

# JSON Export Structure
{
    "export_date": "2025-10-20T10:30:00",
    "date_range": {"start": "2025-10-01", "end": "2025-10-20"},
    "sessions": [
        {
            "date": "2025-10-20",
            "work_time_minutes": 480,
            "break_time_minutes": 60,
            "productive_time_minutes": 420,
            "overtime_minutes": 0,
            "actions": [...],
            "break_periods": [...]
        }
    ],
    "summary": {
        "total_days": 20,
        "average_work_time": 445,
        "total_overtime": 120
    }
}
```

## Error Handling Strategy

### 1. Database Errors
- **Connection Failures**: Retry with exponential backoff
- **Corruption Detection**: Automatic backup restoration
- **Transaction Failures**: Rollback and user notification

### 2. Time Calculation Errors
- **Clock Changes**: Detect and handle daylight saving time
- **System Sleep**: Track suspension periods
- **Invalid States**: Automatic state correction

### 3. GUI Errors
- **Threading Issues**: Proper thread synchronization
- **Memory Leaks**: Regular cleanup and garbage collection
- **Display Errors**: Graceful degradation and error reporting

## Performance Considerations

### 1. Database Optimization
- **Indexes**: Create indexes on frequently queried columns
- **Batch Operations**: Group multiple operations
- **Connection Pooling**: Reuse database connections

### 2. GUI Responsiveness
- **Background Threading**: Move heavy operations off main thread
- **Lazy Loading**: Load data only when needed
- **Efficient Updates**: Update only changed elements

### 3. Memory Management
- **Data Structures**: Use appropriate data types
- **Cleanup**: Regular garbage collection
- **Caching**: Cache frequently accessed data

## Security Considerations

### 1. Data Protection
- **Local Storage**: All data stored locally on user machine
- **File Permissions**: Restrict access to application files
- **Backup Encryption**: Optional encryption for sensitive data

### 2. Input Validation
- **Date Validation**: Ensure valid date formats
- **Time Validation**: Check for reasonable time values
- **File Path Validation**: Prevent directory traversal

## Testing Strategy

### 1. Unit Tests
- **Core Logic**: Test all business logic functions
- **Database Operations**: Test CRUD operations
- **Time Calculations**: Test edge cases and accuracy

### 2. Integration Tests
- **GUI Integration**: Test GUI components with core logic
- **Database Integration**: Test complete data flow
- **Export Integration**: Test export functionality

### 3. User Acceptance Tests
- **Common Workflows**: Test typical user scenarios
- **Error Scenarios**: Test error handling and recovery
- **Performance Tests**: Test responsiveness and memory usage

This technical specification provides the detailed blueprint for implementing the worklog manager application with all required features and considerations for robustness, performance, and maintainability.