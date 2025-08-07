"""
Video Processor for Video-to-Blog Automation System

This module handles all video file operations including:
- Video file validation
- Metadata extraction
- Thumbnail generation
- Video compression
- File information retrieval

Input Types:
- file_path: String - Path to video file
- video_id: String - Video ID for database lookup
- output_path: String - Output path for processed files
- target_size_mb: Integer - Target file size for compression

Output Types:
- is_valid: Boolean
- duration: Integer (seconds)
- file_size: Integer (bytes)
- resolution: Object {width: Integer, height: Integer}
- extension: String
- error: String (if validation fails)

Author: Your Name
Date: 2024
"""

import os
import subprocess
import logging
from typing import Dict, Any, Optional
from flask import jsonify

from db import get_db_client

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Utility class for video file operations"""
    
    def __init__(self):
        """Initialize video processor"""
        self.db_client = get_db_client()
    
    def validate_video_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate video file and extract metadata
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dict[str, Any]: Validation result with metadata
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'is_valid': False,
                    'error': 'File does not exist'
                }
            
            # Check file size
            file_size = os.path.getsize(file_path)
            max_size = 500 * 1024 * 1024  # 500MB
            
            if file_size > max_size:
                return {
                    'is_valid': False,
                    'error': f'File too large: {file_size / (1024*1024):.1f}MB (max: 500MB)'
                }
            
            # Check file extension
            allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension not in allowed_extensions:
                return {
                    'is_valid': False,
                    'error': f'Invalid file type: {file_extension}'
                }
            
            # Get video duration using ffprobe
            duration = self._get_video_duration(file_path)
            
            # Get video resolution
            resolution = self._get_video_resolution(file_path)
            
            return {
                'is_valid': True,
                'duration': duration,
                'file_size': file_size,
                'resolution': resolution,
                'extension': file_extension
            }
            
        except Exception as e:
            logger.error(f"Error validating video file: {str(e)}")
            return {
                'is_valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def get_video_info_by_id(self, video_id: str) -> Dict[str, Any]:
        """
        Get video information by ID from database
        
        Args:
            video_id: Video ID
            
        Returns:
            Dict[str, Any]: Video information
        """
        try:
            # Get video record from database
            response = self.db_client.table('video_files').select('*').eq('id', video_id).execute()
            
            if not response.data:
                return jsonify({'error': 'Video not found'}), 404
            
            video_record = response.data[0]
            file_path = video_record['file_path']
            
            # Get additional video info if file exists
            if os.path.exists(file_path):
                video_info = self._get_comprehensive_video_info(file_path)
                video_info.update(video_record)
            else:
                video_info = video_record
                video_info['file_exists'] = False
            
            return jsonify(video_info), 200
            
        except Exception as e:
            logger.error(f"Error getting video info by ID: {str(e)}")
            return jsonify({'error': 'Failed to get video info'}), 500
    
    def generate_thumbnail(self, file_path: str, output_path: str, time_position: str = "00:00:10") -> bool:
        """
        Generate thumbnail from video
        
        Args:
            file_path: Path to video file
            output_path: Path for thumbnail output
            time_position: Time position for thumbnail (HH:MM:SS)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', file_path,
                '-ss', time_position,
                '-vframes', '1',
                '-vf', 'scale=320:240',
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"Thumbnail generated: {output_path}")
                return True
            else:
                logger.error(f"Failed to generate thumbnail: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout generating thumbnail")
            return False
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return False
    
    def compress_video(self, input_path: str, output_path: str, target_size_mb: int = 50) -> bool:
        """
        Compress video to target file size
        
        Args:
            input_path: Path to input video file
            output_path: Path for compressed video output
            target_size_mb: Target file size in MB
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get original file size
            original_size = os.path.getsize(input_path)
            target_size = target_size_mb * 1024 * 1024
            
            if original_size <= target_size:
                logger.info("Video already within target size")
                return True
            
            # Calculate bitrate for target size
            duration = self._get_video_duration(input_path)
            if not duration:
                return False
            
            # Estimate bitrate (simplified calculation)
            target_bitrate = int((target_size * 8) / duration)
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:v', f'{target_bitrate}',
                '-maxrate', f'{target_bitrate}',
                '-bufsize', f'{target_bitrate * 2}',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            
            if result.returncode == 0:
                compressed_size = os.path.getsize(output_path)
                logger.info(f"Video compressed: {original_size / (1024*1024):.1f}MB -> {compressed_size / (1024*1024):.1f}MB")
                return True
            else:
                logger.error(f"Failed to compress video: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout compressing video")
            return False
        except Exception as e:
            logger.error(f"Error compressing video: {str(e)}")
            return False
    
    def cleanup_temp_files(self, file_paths: list) -> None:
        """
        Clean up temporary files
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {str(e)}")
    
    def _get_video_duration(self, file_path: str) -> Optional[int]:
        """Get video duration in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return int(duration)
            else:
                logger.warning(f"Failed to get video duration: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting video duration")
            return None
        except Exception as e:
            logger.error(f"Error getting video duration: {str(e)}")
            return None
    
    def _get_video_resolution(self, file_path: str) -> Optional[Dict[str, int]]:
        """Get video resolution using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'csv=p=0',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if ',' in output:
                    width, height = map(int, output.split(','))
                    return {'width': width, 'height': height}
            
            return None
            
        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting video resolution")
            return None
        except Exception as e:
            logger.error(f"Error getting video resolution: {str(e)}")
            return None
    
    def _get_comprehensive_video_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive video information"""
        try:
            info = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'duration': self._get_video_duration(file_path),
                'resolution': self._get_video_resolution(file_path),
                'extension': os.path.splitext(file_path)[1].lower(),
                'file_exists': True
            }
            
            # Get additional metadata using ffprobe
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                metadata = json.loads(result.stdout)
                
                # Extract useful information
                format_info = metadata.get('format', {})
                streams = metadata.get('streams', [])
                
                info.update({
                    'format_name': format_info.get('format_name'),
                    'bit_rate': format_info.get('bit_rate'),
                    'video_streams': len([s for s in streams if s.get('codec_type') == 'video']),
                    'audio_streams': len([s for s in streams if s.get('codec_type') == 'audio'])
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {'error': str(e)} 