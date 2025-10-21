"""
Simple Backup Manager for Worklog Manager Application

Provides basic backup functionality without external dependencies.
Uses Python's built-in threading for simple scheduled backups.
"""

import os
import shutil
import sqlite3
import json
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from utils.datetime_compat import datetime_fromisoformat

class BackupManager:
    """Simple backup manager using only built-in Python libraries."""
    
    def __init__(self, db_path: str = None):
        """Initialize backup manager."""
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        if db_path is None:
            # Default to main database location in project root
            root_db = os.path.join(self.project_root, "worklog.db")
            data_db = os.path.join(self.project_root, "data", "worklog.db")

            if os.path.exists(root_db):
                db_path = root_db
            elif os.path.exists(data_db):
                db_path = data_db
            else:
                # Fall back to root path; database layer will create it on demand
                db_path = root_db

        self.db_path = db_path
        self.backup_dir = os.path.join(self.project_root, "backups")
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Background thread management
        self.backup_thread = None
        self.running = False
        
    def create_backup(self, backup_type: str = 'manual', 
                      backup_directory: Optional[str] = None) -> Optional[str]:
        """Create a simple backup of the database.

        Args:
            backup_type: Descriptive label for the backup (e.g. manual, auto).
            backup_directory: Optional override for the destination directory.
        """
        try:
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_dir = backup_directory or self.backup_dir
            os.makedirs(target_dir, exist_ok=True)

            safe_type = (backup_type or 'manual').strip().replace(' ', '_')
            if not safe_type:
                safe_type = 'manual'

            backup_filename = f"worklog_backup_{safe_type}_{timestamp}.db"
            backup_path = os.path.join(target_dir, backup_filename)
            
            # Copy database file if it exists
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                
                # Create backup info file
                info_path = backup_path.replace('.db', '_info.json')
                backup_info = {
                    'created': datetime.now().isoformat(),
                    'original_path': self.db_path,
                    'backup_path': backup_path,
                    'size_bytes': os.path.getsize(backup_path),
                    'type': 'database_backup',
                    'backup_type': safe_type
                }
                
                with open(info_path, 'w') as f:
                    json.dump(backup_info, f, indent=2)
                
                print(f"Backup created: {backup_filename}")
                return backup_path
            else:
                print("Database file not found, backup not created")
                return None
                
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def setup_automatic_backup(self, interval_hours: int = 24):
        """Setup automatic backup with simple interval-based scheduling."""
        if self.backup_thread and self.running:
            self.stop_automatic_backup()
        
        self.running = True
        
        def backup_worker():
            while self.running:
                try:
                    # Wait for the specified interval
                    time.sleep(interval_hours * 3600)  # Convert hours to seconds
                    
                    if self.running:  # Check if still running after sleep
                        self.create_backup()
                        self.cleanup_old_backups()
                        
                except Exception as e:
                    print(f"Error in backup worker: {e}")
        
        self.backup_thread = threading.Thread(target=backup_worker, daemon=True)
        self.backup_thread.start()
        
        print(f"Automatic backup scheduled every {interval_hours} hours")
    
    def stop_automatic_backup(self):
        """Stop automatic backup."""
        self.running = False
        if self.backup_thread:
            self.backup_thread = None
        print("Automatic backup stopped")
    
    def cleanup_old_backups(self, max_backups: int = 10):
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            # Get all backup files
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('worklog_backup_') and filename.endswith('.db'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getctime(filepath)))
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            if len(backup_files) > max_backups:
                for filepath, _ in backup_files[max_backups:]:
                    try:
                        os.remove(filepath)
                        # Also remove info file if it exists
                        info_file = filepath.replace('.db', '_info.json')
                        if os.path.exists(info_file):
                            os.remove(info_file)
                        print(f"Removed old backup: {os.path.basename(filepath)}")
                    except Exception as e:
                        print(f"Error removing old backup {filepath}: {e}")
                        
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")
    
    def list_backups(self) -> List[Dict]:
        """List available backups."""
        backups = []
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('worklog_backup_') and filename.endswith('.db'):
                    filepath = os.path.join(self.backup_dir, filename)
                    info_path = filepath.replace('.db', '_info.json')
                    
                    backup_info = {
                        'filename': filename,
                        'path': filepath,
                        'size': os.path.getsize(filepath),
                        'created': datetime.fromtimestamp(os.path.getctime(filepath))
                    }
                    
                    # Load additional info if available
                    if os.path.exists(info_path):
                        try:
                            with open(info_path, 'r') as f:
                                extra_info = json.load(f)
                                backup_info.update(extra_info)
                        except:
                            pass
                    
                    backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x.get('created', datetime.min), reverse=True)
            
        except Exception as e:
            print(f"Error listing backups: {e}")
        
        return backups

    def get_backup_list(self) -> List[Dict]:
        """Return backup metadata in the format expected by the settings dialog."""
        backups = []

        if not os.path.exists(self.backup_dir):
            return backups

        for filename in os.listdir(self.backup_dir):
            if not filename.startswith('worklog_backup_'):
                continue

            filepath = os.path.join(self.backup_dir, filename)

            if not os.path.isfile(filepath):
                continue

            try:
                stat = os.stat(filepath)
                created_dt = datetime.fromtimestamp(stat.st_mtime)

                entry: Dict = {
                    'name': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'created': created_dt,
                    'type': 'file'
                }

                # Load metadata from the companion info file if available
                info_path = filepath.replace('.db', '_info.json')
                if os.path.exists(info_path):
                    try:
                        with open(info_path, 'r') as info_file:
                            info_data = json.load(info_file)

                        entry['metadata'] = info_data

                        backup_type = info_data.get('backup_type')
                        if backup_type:
                            entry['backup_type'] = backup_type

                        info_created = info_data.get('created')
                        if info_created:
                            try:
                                entry['created'] = datetime_fromisoformat(info_created)
                            except ValueError:
                                pass
                    except Exception as info_error:
                        print(f"Error reading backup info for {filename}: {info_error}")
                else:
                    parts = filename.split('_')
                    if len(parts) >= 3:
                        entry['backup_type'] = parts[2]

                backups.append(entry)

            except Exception as file_error:
                print(f"Error collecting backup info for {filename}: {file_error}")

        backups.sort(key=lambda item: item['created'], reverse=True)
        return backups
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            if not os.path.exists(backup_path):
                print(f"Backup file not found: {backup_path}")
                return False
            
            # Create a backup of current database first
            if os.path.exists(self.db_path):
                current_backup = self.db_path + ".before_restore"
                shutil.copy2(self.db_path, current_backup)
                print(f"Current database backed up to: {current_backup}")
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            print(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def get_backup_status(self) -> Dict:
        """Get current backup system status."""
        return {
            'backup_directory': self.backup_dir,
            'database_path': self.db_path,
            'database_exists': os.path.exists(self.db_path),
            'backup_count': len([f for f in os.listdir(self.backup_dir) 
                                if f.startswith('worklog_backup_') and f.endswith('.db')]),
            'automatic_backup_running': self.running,
            'last_backup': self._get_last_backup_time()
        }
    
    def _get_last_backup_time(self) -> Optional[str]:
        """Get the timestamp of the last backup."""
        try:
            backups = self.list_backups()
            if backups:
                return backups[0]['created'].isoformat()
        except:
            pass
        return None