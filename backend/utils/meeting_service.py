"""
Meeting Service for Video-to-Blog Automation System

This module handles all meeting management operations including:
- Getting meeting details
- Getting processing status
- Listing meetings by organization
- Meeting data retrieval

Input Types:
- meeting_id: String (path parameter)
- organization_id: String (query parameter)
- limit: Integer (query parameter, optional)
- offset: Integer (query parameter, optional)

Output Types:
- meeting_id: String
- title: String
- transcription_status: String
- created_at: String
- meetings: Array of meeting objects
- total: Integer
- limit: Integer
- offset: Integer

Author: Your Name
Date: 2024
"""

from flask import jsonify
import logging
from typing import Dict, Any, Tuple, List

from db import get_db_client

logger = logging.getLogger(__name__)

class MeetingService:
    """Service class for meeting management operations"""
    
    def __init__(self):
        """Initialize meeting service"""
        self.db_client = get_db_client()
    
    def get_processing_status(self, meeting_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get processing status for a meeting
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
        """
        try:
            # Get meeting details
            meeting = self._get_meeting_by_id(meeting_id)
            
            if not meeting:
                return jsonify({'error': 'Meeting not found'}), 404
            
            return jsonify({
                'meeting_id': meeting['id'],
                'title': meeting['title'],
                'transcription_status': meeting.get('transcription_status', 'pending'),
                'created_at': meeting['created_at']
            }), 200
            
        except Exception as e:
            logger.error(f"Get processing status error: {str(e)}")
            return jsonify({'error': 'Failed to get processing status'}), 500
    
    def get_meetings(self, organization_id: str, limit: int = 10, offset: int = 0) -> Tuple[Dict[str, Any], int]:
        """
        Get all meetings for an organization
        
        Args:
            organization_id: Organization ID
            limit: Number of meetings to return
            offset: Number of meetings to skip
            
        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
        """
        try:
            meetings = self._get_meetings_by_organization(organization_id, limit, offset)
            total = self._get_meetings_count(organization_id)
            
            return jsonify({
                'meetings': meetings,
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200
            
        except Exception as e:
            logger.error(f"Get meetings error: {str(e)}")
            return jsonify({'error': 'Failed to get meetings'}), 500
    
    def get_meeting(self, meeting_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get specific meeting details
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
        """
        try:
            meeting = self._get_meeting_by_id(meeting_id)
            
            if not meeting:
                return jsonify({'error': 'Meeting not found'}), 404
            
            # Get related data
            video_files = self._get_video_files_by_meeting(meeting_id)
            blog_posts = self._get_blog_posts_by_meeting(meeting_id)
            processing_logs = self._get_processing_logs_by_meeting(meeting_id)
            
            meeting_data = {
                'meeting': meeting,
                'video_files': video_files,
                'blog_posts': blog_posts,
                'processing_logs': processing_logs
            }
            
            return jsonify(meeting_data), 200
            
        except Exception as e:
            logger.error(f"Get meeting error: {str(e)}")
            return jsonify({'error': 'Failed to get meeting'}), 500
    
    def _get_meeting_by_id(self, meeting_id: str) -> Dict[str, Any]:
        """Get meeting by ID from database"""
        try:
            response = self.db_client.table('meetings').select('*').eq('id', meeting_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting meeting by ID: {str(e)}")
            raise
    
    def _get_meetings_by_organization(self, organization_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get meetings by organization with pagination"""
        try:
            response = self.db_client.table('meetings')\
                .select('*')\
                .eq('organization_id', organization_id)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting meetings by organization: {str(e)}")
            raise
    
    def _get_meetings_count(self, organization_id: str) -> int:
        """Get total count of meetings for organization"""
        try:
            response = self.db_client.table('meetings')\
                .select('count', count='exact')\
                .eq('organization_id', organization_id)\
                .execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error getting meetings count: {str(e)}")
            raise
    
    def _get_video_files_by_meeting(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get video files for a meeting"""
        try:
            response = self.db_client.table('video_files')\
                .select('*')\
                .eq('meeting_id', meeting_id)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting video files by meeting: {str(e)}")
            raise
    
    def _get_blog_posts_by_meeting(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get blog posts for a meeting"""
        try:
            response = self.db_client.table('blog_posts')\
                .select('*')\
                .eq('meeting_id', meeting_id)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting blog posts by meeting: {str(e)}")
            raise
    
    def _get_processing_logs_by_meeting(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get processing logs for a meeting"""
        try:
            response = self.db_client.table('processing_logs')\
                .select('*')\
                .eq('meeting_id', meeting_id)\
                .order('created_at', desc=True)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting processing logs by meeting: {str(e)}")
            raise 