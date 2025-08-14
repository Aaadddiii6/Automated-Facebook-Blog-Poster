"""
Meeting Service for Blog Automation System

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
    
    def get_meetings_with_transcripts(self, organization_id: str = None, limit: int = 100, offset: int = 0) -> Tuple[Dict[str, Any], int]:
        """
        Get meetings that have completed transcripts, optionally filtered by organization.

        Args:
            organization_id: Organization ID (optional)
            limit: Number of meetings to return
            offset: Number of meetings to skip

        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
        """
        try:
            # First get meeting IDs that have transcripts in meeting_minutes table
            minutes_query = self.db_client.table('meeting_minutes') \
                .select('meeting_id,transcript,summary,created_at') \
                .not_.is_('transcript', 'null') \
                .neq('transcript', '') \
                .order('created_at', desc=True)
            
            minutes_response = minutes_query.execute()
            
            if not minutes_response.data:
                return jsonify({
                    'meetings': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset
                }), 200
            
            # Get unique meeting IDs that have transcripts
            meeting_ids = list(set([m['meeting_id'] for m in minutes_response.data if m.get('meeting_id')]))
            
            if not meeting_ids:
                return jsonify({
                    'meetings': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset
                }), 200
            
            # Now get meeting details for these IDs
            meetings_query = self.db_client.table('meetings') \
                .select('id,title,created_at,organization_id') \
                .in_('id', meeting_ids) \
                .order('created_at', desc=True)
            
            if organization_id:
                meetings_query = meetings_query.eq('organization_id', organization_id)
            
            if limit is not None and offset is not None:
                meetings_query = meetings_query.range(offset, offset + limit - 1)
            
            meetings_response = meetings_query.execute()
            
            # Get total count for pagination
            count_query = self.db_client.table('meetings') \
                .select('count', count='exact') \
                .in_('id', meeting_ids)
            if organization_id:
                count_query = count_query.eq('organization_id', organization_id)
            total = count_query.execute().count or 0
            
            # Combine meeting data with transcript info
            meetings = []
            for meeting in (meetings_response.data or []):
                # Find corresponding transcript
                transcript_data = next((m for m in minutes_response.data if m['meeting_id'] == meeting['id']), None)
                if transcript_data:
                    meeting['transcript'] = transcript_data.get('transcript', '')
                    meeting['summary'] = transcript_data.get('summary', '')
                    meeting['transcript_created_at'] = transcript_data.get('created_at', '')
                    meetings.append(meeting)
            
            return jsonify({
                'meetings': meetings,
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200

        except Exception as e:
            logger.error(f"Get meetings with transcripts error: {str(e)}")
            return jsonify({'error': 'Failed to get meetings with transcripts'}), 500

    def get_transcribed_meeting_options(self, organization_id: str = None, limit: int = 100, offset: int = 0) -> Tuple[Dict[str, Any], int]:
        """
        Get compact option list for dropdowns: [{ value, label }]

        Args:
            organization_id: Organization ID (optional)
            limit: Number of options to return
            offset: Number of options to skip

        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
        """
        try:
            # First get meeting IDs that have transcripts in meeting_minutes table
            minutes_query = self.db_client.table('meeting_minutes') \
                .select('meeting_id,transcript') \
                .not_.is_('transcript', 'null') \
                .neq('transcript', '') \
                .order('created_at', desc=True)
            
            minutes_response = minutes_query.execute()
            
            if not minutes_response.data:
                return jsonify({
                    'options': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset
                }), 200
            
            # Get unique meeting IDs that have transcripts
            meeting_ids = list(set([m['meeting_id'] for m in minutes_response.data if m.get('meeting_id')]))
            
            if not meeting_ids:
                return jsonify({
                    'options': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset
                }), 200
            
            # Now get meeting details for these IDs
            meetings_query = self.db_client.table('meetings') \
                .select('id,title,created_at,organization_id') \
                .in_('id', meeting_ids) \
                .order('created_at', desc=True)
            
            if organization_id:
                meetings_query = meetings_query.eq('organization_id', organization_id)
            
            if limit is not None and offset is not None:
                meetings_query = meetings_query.range(offset, offset + limit - 1)
            
            meetings_response = meetings_query.execute()
            
            # Create dropdown options
            options = []
            for meeting in (meetings_response.data or []):
                title = meeting.get('title') or f"Meeting {meeting['id'][:8]}"
                options.append({
                    'value': meeting['id'], 
                    'label': title,
                    'organization_id': meeting.get('organization_id')
                })
            
            return jsonify({
                'options': options,
                'total': len(options),
                'limit': limit,
                'offset': offset
            }), 200

        except Exception as e:
            logger.error(f"Get transcribed meeting options error: {str(e)}")
            return jsonify({'error': 'Failed to get transcribed meeting options'}), 500

    def get_organization_options(self) -> Tuple[Dict[str, Any], int]:
        """
        Get compact organization options for dropdowns: [{ value, label }]

        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
        """
        try:
            # Get all unique organization IDs from meetings table
            response = self.db_client.table('meetings') \
                .select('organization_id') \
                .not_.is_('organization_id', 'null') \
                .execute()
            
            if not response.data:
                return jsonify({
                    'options': [],
                    'total': 0
                }), 200
            
            # Get unique organization IDs, filtering out empty strings and None values
            org_ids = list(set([
                m['organization_id'] for m in response.data 
                if m.get('organization_id') and m['organization_id'].strip() != ''
            ]))
            
            # Create dropdown options
            options = []
            for org_id in org_ids:
                # Get organization name if available, otherwise use ID
                org_response = self.db_client.table('organizations') \
                    .select('name') \
                    .eq('id', org_id) \
                    .execute()
                
                if org_response.data and org_response.data[0].get('name'):
                    label = org_response.data[0]['name']
                else:
                    label = f"Organization {org_id[:8]}..."
                
                options.append({
                    'value': org_id,
                    'label': label
                })
            
            # Sort by label
            options.sort(key=lambda x: x['label'])
            
            return jsonify({
                'options': options,
                'total': len(options)
            }), 200

        except Exception as e:
            logger.error(f"Get organization options error: {str(e)}")
            return jsonify({'error': 'Failed to get organization options'}), 500

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
            blog_posts = self._get_blog_posts_by_meeting(meeting_id)
            processing_logs = self._get_processing_logs_by_meeting(meeting_id)
            
            meeting_data = {
                'meeting': meeting,
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