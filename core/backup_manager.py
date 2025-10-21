"""
Backup Manager for Worklog Manager Application

Handles automatic backups, scheduled exports, and data recovery operations.
Supports multiple backup strategies and retention policies.
"""

import os
import shutil
import sqlite3
import json
import threading
import time
import zipfile
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from pathlib import Path
class BackupManager:
    """Manages automatic backups and data recovery for the worklog application."""
    
    def __init__(self, db_path: str, backup_settings: Dict = None):
        self.db_path = db_path
        self.backup_settings = backup_settings or self.get_default_settings()
        self.backup_thread = None
        self.running = False
        self.next_backup_time = None
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_settings['backup_directory'], exist_ok=True)
        
        # Calculate next backup time
        self._calculate_next_backup_time()
    
    def get_default_settings(self) -> Dict:
        """Get default backup settings."""
        return {
            'backup_directory': os.path.join(os.path.dirname(self.db_path), 'backups'),
            'auto_backup_enabled': True,
            'backup_frequency': 'daily',  # daily, weekly, monthly
            'backup_time': '23:00',  # HH:MM format
            'max_backup_files': 30,
            'compress_backups': True,
            'backup_on_exit': True,
            'backup_on_start': False,
            'include_exports': True,
            'include_settings': True,
            'retention_days': 90
        }
    
    def start_backup_service(self):
        """Start the backup service in a background thread."""
        if not self.running:
            self.running = True
            self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
            self.backup_thread.start()
    
    def stop_backup_service(self):
        """Stop the backup service."""
        self.running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
    
    def _backup_loop(self):
        """Main backup loop running in background thread."""
        while self.running:
            try:
                # Check and run scheduled backups
                self.scheduler.run_pending()
                
                # Sleep for a minute before checking again
                time.sleep(60)
                
            except Exception as e:
                print(f"Error in backup loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def setup_scheduled_backups(self):
        """Setup scheduled backups based on settings."""
        # Clear existing jobs
        self.scheduler.clear()
        
        if not self.backup_settings.get('auto_backup_enabled', True):
            return
        
        frequency = self.backup_settings.get('backup_frequency', 'daily')
        backup_time = self.backup_settings.get('backup_time', '23:00')
        
        try:
            if frequency == 'daily':
                self.scheduler.every().day.at(backup_time).do(self.create_scheduled_backup)
            elif frequency == 'weekly':
                self.scheduler.every().week.at(backup_time).do(self.create_scheduled_backup)
            elif frequency == 'monthly':
                # Monthly on the 1st day at specified time
                self.scheduler.every().month.at(backup_time).do(self.create_scheduled_backup)
        except Exception as e:
            print(f"Error setting up scheduled backup: {e}")
    
    def create_backup(self, backup_type: str = 'manual') -> str:
        """Create a backup of the database and related files."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"worklog_backup_{backup_type}_{timestamp}"
            
            if self.backup_settings.get('compress_backups', True):
                backup_path = os.path.join(
                    self.backup_settings['backup_directory'],
                    f"{backup_name}.zip"
                )
                return self._create_compressed_backup(backup_path, backup_type)
            else:
                backup_path = os.path.join(
                    self.backup_settings['backup_directory'],
                    backup_name
                )
                os.makedirs(backup_path, exist_ok=True)
                return self._create_folder_backup(backup_path, backup_type)
                
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def _create_compressed_backup(self, backup_path: str, backup_type: str) -> str:
        """Create a compressed ZIP backup."""
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database file
            if os.path.exists(self.db_path):
                zipf.write(self.db_path, 'worklog.db')
            
            # Add settings if enabled
            if self.backup_settings.get('include_settings', True):
                settings_dir = os.path.join(os.path.dirname(self.db_path), 'settings')
                if os.path.exists(settings_dir):
                    for root, dirs, files in os.walk(settings_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('settings', 
                                                 os.path.relpath(file_path, settings_dir))
                            zipf.write(file_path, arcname)
            
            # Add exports if enabled
            if self.backup_settings.get('include_exports', True):
                exports_dir = os.path.join(os.path.dirname(self.db_path), 'exports')
                if os.path.exists(exports_dir):
                    for root, dirs, files in os.walk(exports_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('exports', 
                                                 os.path.relpath(file_path, exports_dir))
                            zipf.write(file_path, arcname)
            
            # Add backup metadata
            metadata = {
                'backup_type': backup_type,
                'timestamp': datetime.now().isoformat(),
                'db_path': self.db_path,
                'backup_settings': self.backup_settings,
                'version': '1.0'
            }
            
            zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))
        
        return backup_path
    
    def _create_folder_backup(self, backup_path: str, backup_type: str) -> str:
        """Create a folder-based backup."""
        # Copy database file
        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, os.path.join(backup_path, 'worklog.db'))
        
        # Copy settings if enabled
        if self.backup_settings.get('include_settings', True):
            settings_dir = os.path.join(os.path.dirname(self.db_path), 'settings')
            if os.path.exists(settings_dir):
                backup_settings_dir = os.path.join(backup_path, 'settings')
                shutil.copytree(settings_dir, backup_settings_dir)
        
        # Copy exports if enabled
        if self.backup_settings.get('include_exports', True):
            exports_dir = os.path.join(os.path.dirname(self.db_path), 'exports')
            if os.path.exists(exports_dir):
                backup_exports_dir = os.path.join(backup_path, 'exports')
                shutil.copytree(exports_dir, backup_exports_dir)
        
        # Create backup metadata
        metadata = {
            'backup_type': backup_type,
            'timestamp': datetime.now().isoformat(),
            'db_path': self.db_path,
            'backup_settings': self.backup_settings,
            'version': '1.0'
        }
        
        metadata_path = os.path.join(backup_path, 'backup_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return backup_path
    
    def create_scheduled_backup(self):
        """Create a scheduled backup."""
        backup_path = self.create_backup('scheduled')
        if backup_path:
            print(f"Scheduled backup created: {backup_path}")
            self.cleanup_old_backups()
    
    def cleanup_old_backups(self):
        """Remove old backups based on retention settings."""
        try:
            backup_dir = self.backup_settings['backup_directory']
            max_files = self.backup_settings.get('max_backup_files', 30)
            retention_days = self.backup_settings.get('retention_days', 90)
            
            if not os.path.exists(backup_dir):
                return
            
            # Get all backup files
            backup_files = []
            for file in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, file)
                if os.path.isfile(file_path) and file.startswith('worklog_backup_'):
                    stat = os.stat(file_path)
                    backup_files.append((file_path, stat.st_mtime))
                elif os.path.isdir(file_path) and file.startswith('worklog_backup_'):
                    stat = os.stat(file_path)
                    backup_files.append((file_path, stat.st_mtime))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove files older than retention days
            cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
            files_to_remove = []
            
            for file_path, mtime in backup_files:
                if mtime < cutoff_time:
                    files_to_remove.append(file_path)
            
            # Remove excess files (keep only max_files)
            if len(backup_files) > max_files:
                files_to_remove.extend([f[0] for f in backup_files[max_files:]])
            
            # Remove the files/directories
            for file_path in files_to_remove:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Error removing backup file {file_path}: {e}")
                    
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")
    
    def restore_backup(self, backup_path: str, restore_location: str = None) -> bool:
        """Restore from a backup file."""
        try:
            if restore_location is None:
                restore_location = os.path.dirname(self.db_path)
            
            if backup_path.endswith('.zip'):
                return self._restore_from_zip(backup_path, restore_location)
            else:
                return self._restore_from_folder(backup_path, restore_location)
                
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def _restore_from_zip(self, backup_path: str, restore_location: str) -> bool:
        """Restore from a ZIP backup."""
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Extract all files
            zipf.extractall(restore_location)
            
            # Move database file to correct location if needed
            extracted_db = os.path.join(restore_location, 'worklog.db')
            if os.path.exists(extracted_db) and extracted_db != self.db_path:
                shutil.move(extracted_db, self.db_path)
            
            return True
    
    def _restore_from_folder(self, backup_path: str, restore_location: str) -> bool:
        """Restore from a folder backup."""
        # Copy database file
        backup_db = os.path.join(backup_path, 'worklog.db')
        if os.path.exists(backup_db):
            shutil.copy2(backup_db, self.db_path)
        
        # Copy settings
        backup_settings = os.path.join(backup_path, 'settings')
        if os.path.exists(backup_settings):
            restore_settings = os.path.join(restore_location, 'settings')
            if os.path.exists(restore_settings):
                shutil.rmtree(restore_settings)
            shutil.copytree(backup_settings, restore_settings)
        
        # Copy exports
        backup_exports = os.path.join(backup_path, 'exports')
        if os.path.exists(backup_exports):
            restore_exports = os.path.join(restore_location, 'exports')
            if os.path.exists(restore_exports):
                shutil.rmtree(restore_exports)
            shutil.copytree(backup_exports, restore_exports)
        
        return True
    
    def get_backup_list(self) -> List[Dict]:
        """Get list of available backups with metadata."""
        backups = []
        backup_dir = self.backup_settings['backup_directory']
        
        if not os.path.exists(backup_dir):
            return backups
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            
            if item.startswith('worklog_backup_'):
                try:
                    # Get basic file info
                    stat = os.stat(item_path)
                    backup_info = {
                        'path': item_path,
                        'name': item,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime),
                        'type': 'file' if os.path.isfile(item_path) else 'folder'
                    }
                    
                    # Try to get metadata
                    metadata = self._get_backup_metadata(item_path)
                    if metadata:
                        backup_info.update(metadata)
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    print(f"Error reading backup {item}: {e}")
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def _get_backup_metadata(self, backup_path: str) -> Optional[Dict]:
        """Get metadata from a backup."""
        try:
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    if 'backup_metadata.json' in zipf.namelist():
                        metadata_content = zipf.read('backup_metadata.json')
                        return json.loads(metadata_content.decode('utf-8'))
            else:
                metadata_path = os.path.join(backup_path, 'backup_metadata.json')
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        return json.load(f)
        except Exception as e:
            print(f"Error reading backup metadata: {e}")
        
        return None
    
    def verify_backup(self, backup_path: str) -> Dict:
        """Verify the integrity of a backup."""
        result = {
            'valid': False,
            'has_database': False,
            'has_metadata': False,
            'has_settings': False,
            'has_exports': False,
            'errors': []
        }
        
        try:
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    files = zipf.namelist()
                    
                    # Check for database
                    if 'worklog.db' in files:
                        result['has_database'] = True
                    
                    # Check for metadata
                    if 'backup_metadata.json' in files:
                        result['has_metadata'] = True
                    
                    # Check for settings
                    if any(f.startswith('settings/') for f in files):
                        result['has_settings'] = True
                    
                    # Check for exports
                    if any(f.startswith('exports/') for f in files):
                        result['has_exports'] = True
            
            else:
                # Check folder structure
                if os.path.exists(os.path.join(backup_path, 'worklog.db')):
                    result['has_database'] = True
                
                if os.path.exists(os.path.join(backup_path, 'backup_metadata.json')):
                    result['has_metadata'] = True
                
                if os.path.exists(os.path.join(backup_path, 'settings')):
                    result['has_settings'] = True
                
                if os.path.exists(os.path.join(backup_path, 'exports')):
                    result['has_exports'] = True
            
            # Backup is valid if it has at least database and metadata
            result['valid'] = result['has_database'] and result['has_metadata']
            
        except Exception as e:
            result['errors'].append(f"Error verifying backup: {e}")
        
        return result
    
    def update_settings(self, new_settings: Dict):
        """Update backup settings and reconfigure scheduling."""
        self.backup_settings.update(new_settings)
        
        # Recreate backup directory if changed
        os.makedirs(self.backup_settings['backup_directory'], exist_ok=True)
        
        # Update scheduled backups
        self.setup_scheduled_backups()

class ExportScheduler:
    """Manages scheduled exports of worklog data."""
    
    def __init__(self, worklog_manager, export_settings: Dict = None):
        self.worklog_manager = worklog_manager
        self.export_settings = export_settings or self.get_default_settings()
        self.scheduler = schedule
        self.running = False
        self.export_thread = None
        
        self.setup_scheduled_exports()
    
    def get_default_settings(self) -> Dict:
        """Get default export settings."""
        return {
            'auto_export_enabled': False,
            'export_frequency': 'weekly',  # daily, weekly, monthly
            'export_time': '22:00',
            'export_format': 'csv',  # csv, json, pdf
            'export_directory': os.path.join('data', 'scheduled_exports'),
            'export_date_range': 'last_month',  # last_week, last_month, last_quarter
            'cleanup_old_exports': True,
            'max_export_files': 12
        }
    
    def start_export_service(self):
        """Start the export scheduler service."""
        if not self.running:
            self.running = True
            self.export_thread = threading.Thread(target=self._export_loop, daemon=True)
            self.export_thread.start()
    
    def stop_export_service(self):
        """Stop the export scheduler service."""
        self.running = False
        if self.export_thread:
            self.export_thread.join(timeout=5)
    
    def _export_loop(self):
        """Main export loop running in background thread."""
        while self.running:
            try:
                self.scheduler.run_pending()
                time.sleep(60)
            except Exception as e:
                print(f"Error in export loop: {e}")
                time.sleep(300)
    
    def setup_scheduled_exports(self):
        """Setup scheduled exports based on settings."""
        self.scheduler.clear()
        
        if not self.export_settings.get('auto_export_enabled', False):
            return
        
        frequency = self.export_settings.get('export_frequency', 'weekly')
        export_time = self.export_settings.get('export_time', '22:00')
        
        try:
            if frequency == 'daily':
                self.scheduler.every().day.at(export_time).do(self.create_scheduled_export)
            elif frequency == 'weekly':
                self.scheduler.every().week.at(export_time).do(self.create_scheduled_export)
            elif frequency == 'monthly':
                self.scheduler.every().month.at(export_time).do(self.create_scheduled_export)
        except Exception as e:
            print(f"Error setting up scheduled export: {e}")
    
    def create_scheduled_export(self):
        """Create a scheduled export."""
        try:
            # Create export directory
            export_dir = self.export_settings['export_directory']
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            format_type = self.export_settings.get('export_format', 'csv')
            filename = f"worklog_scheduled_{timestamp}.{format_type}"
            file_path = os.path.join(export_dir, filename)
            
            # Determine date range
            date_range = self.export_settings.get('export_date_range', 'last_month')
            start_date, end_date = self._get_date_range(date_range)
            
            # Create export using the worklog manager's export functionality
            if hasattr(self.worklog_manager, 'export_data'):
                success = self.worklog_manager.export_data(
                    file_path, format_type, start_date, end_date
                )
                
                if success:
                    print(f"Scheduled export created: {file_path}")
                    
                    # Cleanup old exports if enabled
                    if self.export_settings.get('cleanup_old_exports', True):
                        self._cleanup_old_exports()
                else:
                    print("Failed to create scheduled export")
            
        except Exception as e:
            print(f"Error creating scheduled export: {e}")
    
    def _get_date_range(self, range_type: str) -> tuple:
        """Get start and end dates for the specified range."""
        now = datetime.now()
        
        if range_type == 'last_week':
            end_date = now - timedelta(days=now.weekday())
            start_date = end_date - timedelta(days=7)
        elif range_type == 'last_month':
            # First day of current month
            end_date = datetime(now.year, now.month, 1) - timedelta(days=1)
            # First day of last month
            start_date = datetime(end_date.year, end_date.month, 1)
        elif range_type == 'last_quarter':
            # Calculate last quarter
            quarter = (now.month - 1) // 3 + 1
            if quarter == 1:
                start_date = datetime(now.year - 1, 10, 1)
                end_date = datetime(now.year - 1, 12, 31)
            else:
                start_month = (quarter - 2) * 3 + 1
                start_date = datetime(now.year, start_month, 1)
                end_month = start_month + 2
                end_date = datetime(now.year, end_month + 1, 1) - timedelta(days=1)
        else:
            # Default to last month
            end_date = datetime(now.year, now.month, 1) - timedelta(days=1)
            start_date = datetime(end_date.year, end_date.month, 1)
        
        return start_date, end_date
    
    def _cleanup_old_exports(self):
        """Remove old scheduled exports."""
        try:
            export_dir = self.export_settings['export_directory']
            max_files = self.export_settings.get('max_export_files', 12)
            
            if not os.path.exists(export_dir):
                return
            
            # Get all scheduled export files
            export_files = []
            for file in os.listdir(export_dir):
                if file.startswith('worklog_scheduled_'):
                    file_path = os.path.join(export_dir, file)
                    stat = os.stat(file_path)
                    export_files.append((file_path, stat.st_mtime))
            
            # Sort by modification time (newest first)
            export_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove excess files
            if len(export_files) > max_files:
                for file_path, _ in export_files[max_files:]:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing old export {file_path}: {e}")
                        
        except Exception as e:
            print(f"Error cleaning up old exports: {e}")
    
    def update_settings(self, new_settings: Dict):
        """Update export settings and reconfigure scheduling."""
        self.export_settings.update(new_settings)
        
        # Create export directory if needed
        os.makedirs(self.export_settings['export_directory'], exist_ok=True)
        
        # Update scheduled exports
        self.setup_scheduled_exports()