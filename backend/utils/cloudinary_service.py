"""
Cloudinary Service for Video-to-Blog Automation System

This module handles direct uploads to Cloudinary including:
- Video file upload to Cloudinary
- URL generation for external access
- Error handling and retry logic

Input Types:
- file_path: String - Path to local video file
- public_id: String - Public ID for Cloudinary resource
- resource_type: String - Type of resource (video, image, etc.)

Output Types:
- cloudinary_url: String - Public URL for the uploaded file
- cloudinary_id: String - Cloudinary resource ID
- success: Boolean - Upload success status

Author: Your Name
Date: 2024
"""

import os
import logging
from typing import Dict, Any, Optional
import cloudinary
import cloudinary.uploader
import cloudinary.api

logger = logging.getLogger(__name__)

class CloudinaryService:
    """Service class for Cloudinary operations"""
    
    def __init__(self):
        """Initialize Cloudinary service with credentials"""
        try:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
            logger.info("Cloudinary service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudinary service: {str(e)}")
            raise
    
    def upload_video(self, file_path: str, public_id: str) -> Dict[str, Any]:
        """
        Upload video file to Cloudinary
        
        Args:
            file_path: Path to local video file
            public_id: Public ID for the Cloudinary resource
            
        Returns:
            Dict[str, Any]: Upload result with URL and metadata
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File does not exist',
                    'cloudinary_url': None,
                    'cloudinary_id': None
                }
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file_path,
                public_id=public_id,
                resource_type='video',
                overwrite=True,
                invalidate=True
            )
            
            # Extract relevant information
            cloudinary_url = upload_result.get('secure_url')
            cloudinary_id = upload_result.get('public_id')
            
            logger.info(f"Video uploaded to Cloudinary: {cloudinary_id}")
            
            return {
                'success': True,
                'cloudinary_url': cloudinary_url,
                'cloudinary_id': cloudinary_id,
                'file_size': upload_result.get('bytes'),
                'duration': upload_result.get('duration'),
                'format': upload_result.get('format'),
                'width': upload_result.get('width'),
                'height': upload_result.get('height')
            }
            
        except Exception as e:
            logger.error(f"Error uploading video to Cloudinary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'cloudinary_url': None,
                'cloudinary_id': None
            }
    
    def delete_video(self, public_id: str) -> bool:
        """
        Delete video from Cloudinary
        
        Args:
            public_id: Public ID of the Cloudinary resource
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type='video'
            )
            
            if result.get('result') == 'ok':
                logger.info(f"Video deleted from Cloudinary: {public_id}")
                return True
            else:
                logger.error(f"Failed to delete video from Cloudinary: {public_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting video from Cloudinary: {str(e)}")
            return False
    
    def get_video_info(self, public_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video information from Cloudinary
        
        Args:
            public_id: Public ID of the Cloudinary resource
            
        Returns:
            Optional[Dict[str, Any]]: Video information or None
        """
        try:
            result = cloudinary.api.resource(
                public_id,
                resource_type='video'
            )
            
            return {
                'cloudinary_url': result.get('secure_url'),
                'cloudinary_id': result.get('public_id'),
                'file_size': result.get('bytes'),
                'duration': result.get('duration'),
                'format': result.get('format'),
                'width': result.get('width'),
                'height': result.get('height'),
                'created_at': result.get('created_at')
            }
            
        except Exception as e:
            logger.error(f"Error getting video info from Cloudinary: {str(e)}")
            return None 