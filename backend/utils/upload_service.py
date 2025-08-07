"""
Upload Service for Video-to-Blog Automation System

This module handles all video upload operations including:
- File validation and processing
- Database record creation
- Webhook triggering
- Error handling

Input Types:
- video: File upload (multipart/form-data)
- meeting_title: String (optional)
- meeting_date: String (optional)
- organization_id: String (optional)

Output Types:
- success: Boolean
- message: String
- meeting_id: String
- video_id: String
- processing_status: String

Author: Your Name
Date: 2024
"""

from flask import request, jsonify
import os
import uuid
import logging
from datetime import datetime
import asyncio
import requests
from typing import Dict, Any, Tuple

from db import get_db_client
from .video_processor import VideoProcessor
from .validation_service import ValidationService
from .file_manager import FileManager
from .cloudinary_service import CloudinaryService

logger = logging.getLogger(__name__)

class UploadService:
    """Service class for handling video uploads"""
    
    def __init__(self):
        """Initialize upload service with dependencies"""
        self.video_processor = VideoProcessor()
        self.validation_service = ValidationService()
        self.file_manager = FileManager()
        self.db_client = get_db_client()
        self.cloudinary_service = CloudinaryService()
        # Use video upload specific webhook URL if available, fallback to universal webhook
        self.webhook_url = os.getenv('MAKE_VIDEO_UPLOAD_WEBHOOK_URL') or os.getenv('MAKE_WEBHOOK_URL')
    
    async def handle_video_upload(self, request_obj: request) -> Tuple[Dict[str, Any], int]:
        """
        Handle video file upload
        
        Args:
            request_obj: Flask request object containing file and form data
            
        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
            
        Raises:
            ValueError: If file validation fails
            Exception: If upload processing fails
        """
        try:
            # Validate request
            validation_result = self._validate_upload_request(request_obj)
            if not validation_result['is_valid']:
                return jsonify({'error': validation_result['error']}), 400
            
            # Process file upload
            file_data = self._process_file_upload(request_obj)
            
            # Create database records
            meeting_data, video_data = await self._create_database_records(file_data, request_obj)
            
            # Trigger automation webhook
            await self._trigger_webhook(meeting_data, video_data, file_data)
            
            return jsonify({
                'success': True,
                'message': 'Video uploaded successfully',
                'data': {
                    'meeting_id': meeting_data['id'],
                    'title': meeting_data['title']
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Upload processing error: {str(e)}")
            return jsonify({'error': 'Upload failed'}), 500
    
    def _validate_upload_request(self, request_obj: request) -> Dict[str, Any]:
        """
        Validate upload request
        
        Args:
            request_obj: Flask request object
            
        Returns:
            Dict[str, Any]: Validation result with 'is_valid' and 'error' keys
        """
        # Check if file is present
        if 'video' not in request_obj.files:
            return {'is_valid': False, 'error': 'No video file provided'}
        
        file = request_obj.files['video']
        
        # Check if file was selected
        if file.filename == '':
            return {'is_valid': False, 'error': 'No file selected'}
        
        # Validate file extension
        if not self.validation_service.is_valid_video_file(file.filename):
            return {
                'is_valid': False,
                'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv, wmv, flv, webm'
            }
        
        return {'is_valid': True}
    
    def _process_file_upload(self, request_obj: request) -> Dict[str, Any]:
        """
        Process file upload and save to storage
        
        Args:
            request_obj: Flask request object
            
        Returns:
            Dict[str, Any]: File data including path, size, duration, etc.
        """
        file = request_obj.files['video']
        
        # Create unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Save file to storage
        file_path = self.file_manager.save_video_file(file, unique_filename)
        
        # Validate video file
        validation_result = self.video_processor.validate_video_file(file_path)
        if not validation_result['is_valid']:
            # Clean up invalid file
            self.file_manager.delete_file(file_path)
            raise ValueError(validation_result['error'])
        
        return {
            'file_path': file_path,
            'filename': unique_filename,
            'original_filename': file.filename,
            'file_size': validation_result['file_size'],
            'duration': validation_result.get('duration'),
            'resolution': validation_result.get('resolution')
        }
    
    async def _create_database_records(self, file_data: Dict[str, Any], request_obj: request) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Create meeting and video records in database
        
        Args:
            file_data: File information dictionary
            request_obj: Flask request object
            
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: Meeting and video data
        """
        # Get form data
        meeting_title = request_obj.form.get('meeting_title', 'Untitled Meeting')
        organization_id = request_obj.form.get('organization_id', 'default')
        
        # Create meeting record
        meeting_data = {
            'id': str(uuid.uuid4()),
            'title': meeting_title,
            'organization_id': organization_id,
            'meeting_code': f"MEET_{str(uuid.uuid4())[:8]}",
            'scheduled_at': datetime.now().isoformat(),
            'description': request_obj.form.get('meeting_description', ''),
            'created_at': datetime.now().isoformat()
        }
        
        # Create video record (will be updated after Cloudinary upload)
        video_data = {
            'meeting_id': meeting_data['id'],
            'original_filename': file_data['original_filename'],
            'drive_share_link': '',  # Will be updated with Cloudinary URL
            'uploaded_at': datetime.now().isoformat()
        }
        
        # Store in database
        meeting = await self._create_meeting_record(meeting_data)
        video_file = await self._create_video_record(video_data)
        
        return meeting, video_file
    
    async def _create_meeting_record(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create meeting record in database"""
        try:
            response = self.db_client.table('meetings').insert(meeting_data).execute()
            if response.data:
                logger.info(f"Created meeting: {response.data[0]['id']}")
                return response.data[0]
            else:
                raise Exception("Failed to create meeting")
        except Exception as e:
            logger.error(f"Error creating meeting: {str(e)}")
            raise
    
    async def _create_video_record(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create video record in database"""
        try:
            response = self.db_client.table('meeting_videos').insert(video_data).execute()
            if response.data:
                logger.info(f"Created video record for meeting: {video_data['meeting_id']}")
                return response.data[0]
            else:
                raise Exception("Failed to create video record")
        except Exception as e:
            logger.error(f"Error creating video record: {str(e)}")
            raise
    
    async def _trigger_webhook(self, meeting_data: Dict[str, Any], video_data: Dict[str, Any], file_data: Dict[str, Any]) -> None:
        """Trigger Make.com webhook for automation"""
        try:
            # Upload video to Cloudinary first
            cloudinary_public_id = f"{meeting_data['id']}_{file_data['filename']}"
            cloudinary_result = self.cloudinary_service.upload_video(
                file_data['file_path'], 
                cloudinary_public_id
            )
            
            if not cloudinary_result['success']:
                logger.error(f"Cloudinary upload failed: {cloudinary_result.get('error')}")
                # Fallback to local URL
                base_url = os.getenv('BASE_URL', 'http://localhost:3000')
                video_url = f"{base_url}/api/videos/{video_data['id']}/file"
            else:
                video_url = cloudinary_result['cloudinary_url']
                logger.info(f"Video uploaded to Cloudinary: {cloudinary_result['cloudinary_id']}")
                
                # Update video record with Cloudinary URL
                await self._update_video_cloudinary_url(meeting_data['id'], cloudinary_result['cloudinary_url'], cloudinary_result['cloudinary_id'])
            
            webhook_data = {
                'meeting_id': meeting_data['id'],
                'video_url': video_url,  # Cloudinary URL for Assembly AI
                'meeting_title': meeting_data['title'],
                'organization_id': meeting_data['organization_id'],
                'cloudinary_id': cloudinary_result.get('cloudinary_id'),
                'cloudinary_url': cloudinary_result.get('cloudinary_url')
            }
            
            webhook_response = requests.post(
                self.webhook_url,
                json=webhook_data,
                headers={'Content-Type': 'application/json'},
                timeout=300
            )
            
            if webhook_response.status_code != 200:
                logger.warning(f"Webhook call failed: {webhook_response.status_code}")
            else:
                logger.info("Webhook triggered successfully")
                
        except Exception as e:
            logger.error(f"Error triggering webhook: {str(e)}")
            # Don't raise exception - webhook failure shouldn't fail upload
    
    async def _update_video_cloudinary_url(self, meeting_id: str, cloudinary_url: str, cloudinary_id: str) -> None:
        """Update video record with Cloudinary URL"""
        try:
            update_data = {
                'drive_share_link': cloudinary_url
            }
            response = self.db_client.table('meeting_videos').update(update_data).eq('meeting_id', meeting_id).execute()
            if response.data:
                logger.info(f"Updated video with Cloudinary URL: {meeting_id}")
            else:
                logger.warning(f"Failed to update video Cloudinary URL: {meeting_id}")
        except Exception as e:
            logger.error(f"Error updating video Cloudinary URL: {str(e)}")
    
 