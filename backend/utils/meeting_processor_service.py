"""
Meeting Processor Service for Content Generation

This module handles processing of meeting IDs to fetch transcripts from Supabase
and trigger content generation workflow.

Author: Your Name
Date: 2024
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import requests
import os

from db import get_db_client

logger = logging.getLogger(__name__)

class MeetingProcessorService:
    """Service class for processing meeting IDs"""
    
    def __init__(self):
        """Initialize meeting processor service"""
        self.db_client = get_db_client()
        # Use meeting ID specific webhook URL if available, fallback to universal webhook
        self.make_webhook_url = os.getenv('MAKE_MEETING_ID_WEBHOOK_URL') or os.getenv('MAKE_WEBHOOK_URL')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    async def process_meeting_id(self, meeting_id: str, organization_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Process a meeting ID to fetch transcript and trigger content generation
        
        Args:
            meeting_id: Meeting ID from Supabase
            organization_id: Organization ID
            
        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
        """
        try:
            logger.info(f"Processing meeting ID: {meeting_id}")
            
            # Validate meeting ID format
            if not self._is_valid_uuid(meeting_id):
                return {
                    'error': 'Invalid meeting ID format'
                }, 400
            
            # Fetch meeting data from Supabase
            meeting_data = await self._fetch_meeting_from_supabase(meeting_id)
            if not meeting_data:
                return {
                    'error': 'Meeting not found in Supabase'
                }, 404
            
            # Check if meeting has transcript
            if not meeting_data.get('transcript'):
                return {
                    'error': 'Meeting does not have a transcript'
                }, 400
            
            # Create or update meeting record in our database
            local_meeting = await self._create_or_update_meeting(meeting_id, organization_id, meeting_data)
            
            # Trigger content generation webhook
            await self._trigger_content_generation_webhook(local_meeting['id'], meeting_data)
            
            return {
                'success': True,
                'message': 'Meeting processing started successfully',
                'data': {
                    'meeting_id': local_meeting['id'],
                    'supabase_meeting_id': meeting_id,
                    'title': meeting_data.get('title', ''),
                    'transcript_available': True
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error processing meeting ID: {str(e)}")
            return {
                'error': f'Failed to process meeting: {str(e)}'
            }, 500
    
    async def _fetch_meeting_from_supabase(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch meeting data from Supabase
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Optional[Dict[str, Any]]: Meeting data or None if not found
        """
        try:
            # Make request to Supabase API
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # First, fetch the meeting details from meetings table
            meetings_url = f"{self.supabase_url}/rest/v1/meetings?id=eq.{meeting_id}&select=*"
            meetings_response = requests.get(meetings_url, headers=headers)
            
            if meetings_response.status_code != 200:
                logger.error(f"Supabase meetings API error: {meetings_response.status_code} - {meetings_response.text}")
                return None
            
            meetings_data = meetings_response.json()
            if not meetings_data or len(meetings_data) == 0:
                logger.warning(f"Meeting not found in Supabase meetings table: {meeting_id}")
                return None
            
            meeting_info = meetings_data[0]
            
            # Then, fetch the transcript and summary from meeting_minutes table
            minutes_url = f"{self.supabase_url}/rest/v1/meeting_minutes?meeting_id=eq.{meeting_id}&select=*"
            minutes_response = requests.get(minutes_url, headers=headers)
            
            if minutes_response.status_code != 200:
                logger.error(f"Supabase meeting_minutes API error: {minutes_response.status_code} - {minutes_response.text}")
                return None
            
            minutes_data = minutes_response.json()
            if not minutes_data or len(minutes_data) == 0:
                logger.warning(f"Meeting minutes not found in Supabase: {meeting_id}")
                return None
            
            meeting_minutes = minutes_data[0]
            
            # Combine meeting info with transcript and summary
            combined_data = {
                **meeting_info,
                'transcript': meeting_minutes.get('transcript', ''),
                'summary': meeting_minutes.get('summary', ''),
                'minutes_id': meeting_minutes.get('id')
            }
            
            logger.info(f"Fetched meeting and minutes from Supabase: {meeting_id}")
            return combined_data
                
        except Exception as e:
            logger.error(f"Error fetching meeting from Supabase: {str(e)}")
            return None
    
    async def _create_or_update_meeting(self, supabase_meeting_id: str, organization_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update meeting record in local database
        
        Args:
            supabase_meeting_id: Meeting ID from Supabase
            organization_id: Organization ID
            meeting_data: Meeting data from Supabase
            
        Returns:
            Dict[str, Any]: Created/updated meeting record
        """
        try:
            # Check if meeting already exists by title and organization (since we don't have supabase_meeting_id column)
            existing_meeting = self.db_client.table('meetings').select('*').eq('title', meeting_data.get('title', '')).eq('organization_id', organization_id).execute()
            
            meeting_record = {
                'organization_id': organization_id,
                'title': meeting_data.get('title', ''),
                'meeting_code': f"MEET_{str(uuid.uuid4())[:8]}",
                'scheduled_at': datetime.now().isoformat(),
                'description': meeting_data.get('description', ''),
                'updated_at': datetime.now().isoformat()
            }
            
            if existing_meeting.data:
                # Update existing meeting with new transcript
                response = self.db_client.table('meetings').update(meeting_record).eq('id', existing_meeting.data[0]['id']).execute()
                logger.info(f"Updated existing meeting with transcript: {existing_meeting.data[0]['id']}")
                return response.data[0]
            else:
                # Create new meeting
                meeting_record['created_at'] = datetime.now().isoformat()
                response = self.db_client.table('meetings').insert(meeting_record).execute()
                logger.info(f"Created new meeting with transcript: {response.data[0]['id']}")
                return response.data[0]
                
        except Exception as e:
            logger.error(f"Error creating/updating meeting: {str(e)}")
            raise
    
    async def _trigger_content_generation_webhook(self, meeting_id: str, meeting_data: Dict[str, Any]) -> None:
        """
        Trigger content generation webhook for meeting ID flow
        
        Args:
            meeting_id: Local meeting ID
            meeting_data: Meeting data from Supabase
        """
        try:
            if not self.make_webhook_url:
                logger.warning("Make.com webhook URL not configured")
                return
            
            webhook_data = {
                'meeting_id': meeting_id,
                'organisation_id': meeting_data.get('organization_id', ''),
                'source': 'supabase'
            }
            
            response = requests.post(
                self.make_webhook_url,
                json=webhook_data,
                headers={'Content-Type': 'application/json'},
                timeout=300
            )
            
            if response.status_code != 200:
                logger.warning(f"Content generation webhook failed: {response.status_code}")
            else:
                logger.info("Content generation webhook triggered successfully")
                
        except Exception as e:
            logger.error(f"Error triggering content generation webhook: {str(e)}")
            # Don't raise exception - webhook failure shouldn't fail the process
    

    
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """
        Validate UUID format
        
        Args:
            uuid_string: String to validate
            
        Returns:
            bool: True if valid UUID format
        """
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        return bool(uuid_pattern.match(uuid_string)) 