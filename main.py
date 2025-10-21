"""
Worklog Manager - Advanced Daily Work Time Tracking Application

A comprehensive Python GUI application for tracking daily work hours with advanced
features including automatic calculation of productive time, breaks, overtime,
theme management, notifications, backups, and system integration.

Core Features:
- Start/Stop/Continue work sessions
- Break type management (Lunch, Coffee, General)
- Real-time time calculations
- 7.5-hour work norm compliance
- SQLite database storage
- Detailed action logging
- Export functionality (CSV, JSON, PDF)
- Revoke/Undo system

Advanced Features (Phase 4):
- Settings management with persistent configuration
- Theme system (light/dark modes with custom colors)
- Notification system with work reminders and alerts
- Automatic backup system with scheduling
- Keyboard shortcuts (customizable)
- System tray integration
- Comprehensive help system
- Cross-platform compatibility

Author: GitHub Copilot
Version: 1.6.0
"""

import sys
import os
import logging
import threading
import atexit
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import core application components
from gui.main_window import MainWindow
from core.settings import SettingsManager
from core.notification_manager import NotificationManager
from core.simple_backup_manager import BackupManager
from gui.theme_manager import ThemeManager
from gui.system_tray import SystemTrayManager
from gui.keyboard_shortcuts import KeyboardShortcutManager


class WorklogApplication:
    """
    Main application class that coordinates all components.
    
    This class manages the integration of all Phase 4 components:
    - Settings management
    - Theme system
    - Notification system
    - Backup system
    - System tray integration
    - Keyboard shortcuts
    """
    
    def __init__(self):
        """Initialize the application with all components."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize basic managers
        self.settings_manager = SettingsManager()
        
        # Initialize notification manager with default settings
        try:
            settings = self.settings_manager.settings  # Access settings attribute directly
            if hasattr(settings, 'notifications'):
                notification_settings = settings.notifications
            else:
                # Create default notification settings if not available
                from core.settings import NotificationSettings
                notification_settings = NotificationSettings()
            self.notification_manager = NotificationManager(notification_settings)
        except Exception as e:
            self.logger.warning(f"Could not initialize notification manager: {e}")
            self.notification_manager = None
        
        self.backup_manager = BackupManager()
        
        # UI-dependent managers (created later)
        self.theme_manager = None
        self.system_tray_manager = None
        self.keyboard_manager = None
        self.main_window = None
        
        # Setup application
        self._setup_components()
        self._setup_cleanup()
        
    def _setup_components(self):
        """Setup and configure all application components."""
        try:
            # Load settings
            settings = self.settings_manager.settings
            
            # Start notification system
            if self.notification_manager:
                self.notification_manager.start_monitoring()
            
            # Configure backup system
            try:
                if hasattr(settings, 'backup') and settings.backup.auto_backup_enabled:
                    self.backup_manager.setup_automatic_backup(24)  # Daily backup
                else:
                    # Setup default daily backup
                    self.backup_manager.setup_automatic_backup(24)
            except AttributeError:
                # If settings don't have backup config, use defaults
                self.backup_manager.setup_automatic_backup(24)
            
            self.logger.info("All application components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up components: {e}")
            raise
    
    def _setup_cleanup(self):
        """Setup cleanup handlers for graceful shutdown."""
        atexit.register(self.cleanup)
    
    def create_main_window(self):
        """Create and configure the main application window."""
        try:
            # Create main window
            self.main_window = MainWindow()
            
            # Initialize UI-dependent managers after main window exists
            try:
                self.theme_manager = ThemeManager(self.main_window.root)
            except Exception as e:
                self.logger.warning(f"Could not initialize theme manager: {e}")
                self.theme_manager = None
            
            # Setup system tray (after main window exists)
            settings = self.settings_manager.settings
            try:
                if settings.general.system_tray_enabled:
                    self.logger.info("Attempting to initialize system tray...")
                    self.system_tray_manager = SystemTrayManager(self.main_window.root, "Worklog Manager")
                    
                    # Register callbacks for tray menu actions
                    self.system_tray_manager.register_callback("quit_app", self.main_window.quit_application)
                    self.system_tray_manager.register_callback("show_settings", self.main_window.open_settings_from_tray)
                    self.system_tray_manager.register_callback("show_window", self.main_window.show_window)
                    self.system_tray_manager.register_callback("hide_window", self.main_window.hide_window)
                    self.system_tray_manager.register_callback("toggle_window", self.main_window.toggle_window_visibility)
                    
                    self.logger.info("Starting system tray...")
                    if self.system_tray_manager.start_tray():
                        self.logger.info("System tray initialized and started successfully")
                    else:
                        self.logger.warning("System tray could not be started")
                        self.system_tray_manager = None
                else:
                    self.logger.info("System tray is disabled in settings")
            except AttributeError as e:
                # Skip system tray if settings don't support it
                self.logger.warning(f"System tray not available: {e}")
                import traceback
                self.logger.warning(traceback.format_exc())
            except Exception as e:
                self.logger.warning(f"Could not initialize system tray: {e}")
                import traceback
                self.logger.warning(traceback.format_exc())
            
            # Setup keyboard shortcuts
            try:
                self.keyboard_manager = KeyboardShortcutManager(self.main_window)
            except Exception as e:
                self.logger.warning(f"Could not setup keyboard shortcuts: {e}")
            
            # Apply theme to main window
            if self.theme_manager:
                try:
                    settings = self.settings_manager.settings
                    if hasattr(settings, 'appearance'):
                        self.theme_manager.apply_theme(settings.appearance.theme)
                    else:
                        self.theme_manager.apply_theme('light')  # Default theme
                except Exception as e:
                    self.logger.warning(f"Could not apply theme: {e}")
            
            self.logger.info("Main window created and configured")
            return self.main_window
            
        except Exception as e:
            self.logger.error(f"Error creating main window: {e}")
            raise
    
    def run(self):
        """Run the application."""
        try:
            # Create main window
            main_window = self.create_main_window()
            
            # Start the application
            self.logger.info("Starting Worklog Manager Application v1.6.0")
            main_window.run()
            
        except Exception as e:
            self.logger.error(f"Error running application: {e}")
            raise
    
    def cleanup(self):
        """Cleanup resources on application exit."""
        try:
            self.logger.info("Application cleanup started")
            
            # Stop notification monitoring
            if self.notification_manager:
                self.notification_manager.stop_monitoring()
            
            # Cleanup system tray
            if self.system_tray_manager:
                self.system_tray_manager.cleanup()
            
            # Final backup if needed
            try:
                settings = self.settings_manager.settings
                if hasattr(settings, 'backup') and settings.backup.backup_on_exit:
                    self.backup_manager.create_backup()
                else:
                    # Create backup on exit by default
                    self.backup_manager.create_backup()
            except:
                # Always try to create a final backup
                self.backup_manager.create_backup()
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def setup_logging():
    """Setup application logging."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create log filename with current date
    log_filename = f"worklog_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(logs_dir, log_filename)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("="*50)
    logger.info("Worklog Manager Application Starting")
    logger.info(f"Version: 1.6.0")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"Project Root: {project_root}")
    logger.info(f"Log File: {log_path}")
    logger.info("="*50)


def main():
    """Main application entry point with full Phase 4 integration."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Initializing Worklog Manager v1.6.0 with advanced features...")
        
        # Create and run the comprehensive application
        app = WorklogApplication()
        app.run()
        
        logger.info("Application shutdown normally")
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        logging.getLogger(__name__).info("Application interrupted by user")
        
    except Exception as e:
        error_msg = f"Fatal error: {e}"
        print(error_msg)
        logging.getLogger(__name__).critical(error_msg, exc_info=True)
        
        # Show error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Fatal Error", 
                               f"The Worklog Manager encountered a fatal error:\n\n{e}\n\n"
                               f"Please check the log file for more details.\n"
                               f"Log location: logs/worklog_{datetime.now().strftime('%Y%m%d')}.log")
            root.destroy()
        except:
            pass  # If GUI is not available, just exit
        
        sys.exit(1)


if __name__ == "__main__":
    main()