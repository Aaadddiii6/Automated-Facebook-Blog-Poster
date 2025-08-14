"""
Cloudinary Service for Blog Automation System

This module handles direct uploads to Cloudinary including:
- Image upload for blog posts
- URL generation for external access
- Error handling and retry logic

Input Types:
- public_id: String - Public ID for Cloudinary resource
- resource_type: String - Type of resource (image, etc.)

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
    

    

    
 