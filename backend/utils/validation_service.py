"""
Validation Service for Blog Automation System

This module handles all input validation and sanitization including:
- File type validation
- Data format validation
- Input sanitization
- Security validation

Input Types:
- filename: String - File name to validate
- data: Dict[str, Any] - Data to validate
- field_name: String - Field name for validation
- value: Any - Value to validate

Output Types:
- is_valid: Boolean
- error: String (if validation fails)
- sanitized_value: Any (sanitized value)

Author: Your Name
Date: 2024
"""

import re
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class ValidationService:
    """Service class for input validation and sanitization"""
    
    def __init__(self):
        """Initialize validation service"""
        self.max_title_length = 255
        self.max_content_length = 10000
    

    

    
    def validate_meeting_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate meeting data
        
        Args:
            data: Meeting data dictionary
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Validate title
            title = data.get('title', '')
            if not title or len(title.strip()) == 0:
                return False, "Meeting title is required"
            
            if len(title) > self.max_title_length:
                return False, f"Meeting title too long (max {self.max_title_length} characters)"
            
            # Validate organization_id
            organization_id = data.get('organization_id', '')
            if not organization_id or len(organization_id.strip()) == 0:
                return False, "Organization ID is required"
            

            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating meeting data: {str(e)}")
            return False, "Validation error occurred"
    
    def validate_webhook_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate webhook data
        
        Args:
            data: Webhook data dictionary
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Check required fields
            required_fields = ['meeting_id', 'step']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    return False, f"Missing required field: {field}"
            
            # Validate step values
            valid_steps = [
                'transcription_complete',
                'blog_generation_complete',
                'facebook_post_complete',
                'processing_error'
            ]
            
            if data['step'] not in valid_steps:
                return False, f"Invalid step: {data['step']}"
            
            # Validate meeting_id format (should be UUID)
            if not self._is_valid_uuid(data['meeting_id']):
                return False, "Invalid meeting ID format"
            
            # Check for source in data when needed
            if data['step'] in ['transcription_complete', 'processing_error']:
                if 'source' not in data.get('data', {}):
                    return False, "data.source is required for this step"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating webhook data: {str(e)}")
            return False, "Validation error occurred"
    
    def sanitize_string(self, value: str, max_length: int = None) -> str:
        """
        Sanitize string input
        
        Args:
            value: String value to sanitize
            max_length: Maximum length allowed
            
        Returns:
            str: Sanitized string
        """
        if not value:
            return ""
        
        # Remove leading/trailing whitespace
        sanitized = value.strip()
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        # Truncate if too long
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            str: Sanitized filename
        """
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
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if valid email, False otherwise
        """
        if not email:
            return False
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid URL, False otherwise
        """
        if not url:
            return False
        
        # Basic URL regex pattern
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """
        Validate UUID format
        
        Args:
            uuid_string: UUID string to validate
            
        Returns:
            bool: True if valid UUID, False otherwise
        """
        if not uuid_string:
            return False
        
        # UUID regex pattern
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_string.lower()))
    
    def _is_valid_date_format(self, date_string: str) -> bool:
        """
        Validate date format (ISO 8601)
        
        Args:
            date_string: Date string to validate
            
        Returns:
            bool: True if valid date format, False otherwise
        """
        if not date_string:
            return False
        
        # ISO 8601 date regex pattern
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
        return bool(re.match(pattern, date_string)) 