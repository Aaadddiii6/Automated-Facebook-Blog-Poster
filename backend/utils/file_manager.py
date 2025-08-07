"""
File Manager for Video-to-Blog Automation System

This module handles all file system operations including:
- File saving and deletion
- Directory management
- File path operations
- Storage cleanup

Input Types:
- file: File object - File to save
- filename: String - Name for the file
- file_path: String - Path to file
- directory_path: String - Directory path

Output Types:
- file_path: String - Path where file was saved
- success: Boolean - Operation success status
- error: String - Error message if operation fails

Author: Your Name
Date: 2024
"""

import os
import logging
from typing import Optional
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

class FileManager:
    """Utility class for file system operations"""
    
    def __init__(self):
        """Initialize file manager"""
        self.storage_base_path = os.path.join(os.getcwd(), 'storage', 'videos')
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self) -> None:
        """Ensure storage directory exists"""
        try:
            os.makedirs(self.storage_base_path, exist_ok=True)
            logger.info(f"Storage directory ensured: {self.storage_base_path}")
        except Exception as e:
            logger.error(f"Error creating storage directory: {str(e)}")
            raise
    
    def save_video_file(self, file: FileStorage, filename: str) -> str:
        """
        Save video file to storage
        
        Args:
            file: File object to save
            filename: Name for the saved file
            
        Returns:
            str: Path where file was saved
            
        Raises:
            Exception: If file saving fails
        """
        try:
            # Ensure filename is safe
            safe_filename = self._sanitize_filename(filename)
            
            # Create full file path
            file_path = os.path.join(self.storage_base_path, safe_filename)
            
            # Save file
            file.save(file_path)
            
            logger.info(f"Video file saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving video file: {str(e)}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return os.path.exists(file_path)
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to file
            
        Returns:
            Optional[int]: File size in bytes or None if error
        """
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return None
        except Exception as e:
            logger.error(f"Error getting file size for {file_path}: {str(e)}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get comprehensive file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Optional[dict]: File information or None if error
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat_info = os.stat(file_path)
            
            return {
                'path': file_path,
                'size': stat_info.st_size,
                'created': stat_info.st_ctime,
                'modified': stat_info.st_mtime,
                'accessed': stat_info.st_atime,
                'filename': os.path.basename(file_path),
                'extension': os.path.splitext(file_path)[1].lower(),
                'directory': os.path.dirname(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
    
    def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """
        Clean up old files from storage
        
        Args:
            max_age_days: Maximum age of files in days
            
        Returns:
            int: Number of files deleted
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            deleted_count = 0
            
            for filename in os.listdir(self.storage_base_path):
                file_path = os.path.join(self.storage_base_path, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        if self.delete_file(file_path):
                            deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
            return 0
    
    def get_storage_usage(self) -> dict:
        """
        Get storage usage information
        
        Returns:
            dict: Storage usage statistics
        """
        try:
            total_size = 0
            file_count = 0
            
            for filename in os.listdir(self.storage_base_path):
                file_path = os.path.join(self.storage_base_path, filename)
                
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'file_count': file_count,
                'storage_path': self.storage_base_path
            }
            
        except Exception as e:
            logger.error(f"Error getting storage usage: {str(e)}")
            return {
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'file_count': 0,
                'storage_path': self.storage_base_path,
                'error': str(e)
            }
    
    def create_backup(self, source_path: str, backup_directory: str = None) -> Optional[str]:
        """
        Create backup of a file
        
        Args:
            source_path: Path to source file
            backup_directory: Directory for backup (optional)
            
        Returns:
            Optional[str]: Path to backup file or None if failed
        """
        try:
            import shutil
            from datetime import datetime
            
            if not os.path.exists(source_path):
                logger.error(f"Source file not found: {source_path}")
                return None
            
            # Create backup directory if not provided
            if not backup_directory:
                backup_directory = os.path.join(self.storage_base_path, 'backups')
                os.makedirs(backup_directory, exist_ok=True)
            
            # Create backup filename with timestamp
            filename = os.path.basename(source_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{timestamp}_{filename}"
            backup_path = os.path.join(backup_directory, backup_filename)
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
        """
        import re
        
        if not filename:
            return ""
        
        # Remove path separators and other dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:255-len(ext)-1] + (f'.{ext}' if ext else '')
        
        return sanitized 