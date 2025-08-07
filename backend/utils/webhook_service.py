"""
Webhook Service for Video-to-Blog Automation System

This module handles all webhook callbacks from Make.com including:
- Transcription completion
- Blog generation completion
- Facebook posting completion
- Error handling

Input Types:
- meeting_id: String (required)
- video_id: String (required)
- step: String (required) - 'transcription_complete', 'blog_generation_complete', 'facebook_post_complete', 'processing_error'
- data: Object (optional) - Step-specific data
- status: String (optional)
- error: String (optional)

Output Types:
- success: Boolean
- message: String

Author: Your Name
Date: 2024
"""

from flask import request, jsonify
import logging
import asyncio
from typing import Dict, Any, Tuple
from datetime import datetime

from db import get_db_client

logger = logging.getLogger(__name__)

class WebhookService:
    """Service class for handling webhook callbacks"""
    
    def __init__(self):
        """Initialize webhook service"""
        self.db_client = get_db_client()
    
    def handle_webhook(self, request_obj: request) -> Tuple[Dict[str, Any], int]:
        """
        Handle webhook callbacks from Make.com
        
        Args:
            request_obj: Flask request object containing webhook data
            
        Returns:
            Tuple[Dict[str, Any], int]: Response data and HTTP status code
            
        Raises:
            ValueError: If required fields are missing
            Exception: If webhook processing fails
        """
        try:
            # Get webhook data
            webhook_data = request_obj.get_json()
            
            if not webhook_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            validation_result = self._validate_webhook_data(webhook_data)
            if not validation_result['is_valid']:
                return jsonify({'error': validation_result['error']}), 400
            
            # Extract fields
            meeting_id = webhook_data.get('meeting_id')
            video_id = webhook_data.get('video_id')
            step = webhook_data.get('step')
            data = webhook_data.get('data', {})
            status = webhook_data.get('status')
            error = webhook_data.get('error')
            
            logger.info(f"Webhook received: {step} for meeting {meeting_id}")
            
            # Process webhook based on step
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                if step == 'transcription_complete':
                    # Handle both video upload and meeting ID flows
                    loop.run_until_complete(self._handle_transcription_complete(meeting_id, video_id, data))
                    
                elif step == 'blog_generation_complete':
                    loop.run_until_complete(self._handle_blog_generation_complete(meeting_id, data))
                    
                elif step == 'facebook_post_complete':
                    loop.run_until_complete(self._handle_facebook_post_complete(meeting_id, data))
                    
                elif step == 'processing_error':
                    loop.run_until_complete(self._handle_processing_error(meeting_id, video_id, error))
                    
                else:
                    logger.warning(f"Unknown webhook step: {step}")
                    return jsonify({'error': 'Unknown step'}), 400
                    
            finally:
                loop.close()
            
            return jsonify({
                'success': True,
                'message': 'Webhook processed successfully'
            }), 200
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return jsonify({'error': 'Webhook processing failed'}), 500
    
    def _validate_webhook_data(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate webhook data
        
        Args:
            webhook_data: Webhook data dictionary
            
        Returns:
            Dict[str, Any]: Validation result with 'is_valid' and 'error' keys
        """
        # Check required fields
        required_fields = ['meeting_id', 'step']
        
        for field in required_fields:
            if field not in webhook_data or not webhook_data[field]:
                return {
                    'is_valid': False,
                    'error': f'Missing required field: {field}'
                }
        
        # Validate step values
        valid_steps = [
            'transcription_complete',
            'blog_generation_complete',
            'facebook_post_complete',
            'processing_error'
        ]
        
        if webhook_data['step'] not in valid_steps:
            return {
                'is_valid': False,
                'error': f'Invalid step: {webhook_data["step"]}. Valid steps: {", ".join(valid_steps)}'
            }
        
        # Check for video_id when needed (only for video upload flow)
        if webhook_data['step'] in ['transcription_complete', 'processing_error']:
            # Check if this is a video upload flow (has video_id) or meeting ID flow (has source)
            if 'video_id' not in webhook_data and 'source' not in webhook_data.get('data', {}):
                return {
                    'is_valid': False,
                    'error': 'Either video_id or data.source is required for this step'
                }
            
            # If it's a video upload flow, video_id is required
            if 'video_id' in webhook_data and not webhook_data['video_id']:
                return {
                    'is_valid': False,
                    'error': 'video_id is required for video upload flow'
                }
        
        return {'is_valid': True}
    
    async def _handle_transcription_complete(self, meeting_id: str, video_id: str = None, data: Dict[str, Any] = None) -> None:
        """
        Handle transcription completion
        
        Args:
            meeting_id: Meeting ID
            video_id: Video ID (optional for meeting ID flow)
            data: Transcription data containing transcript and summary
        """
        try:
            data = data or {}
            transcript = data.get('transcript', '')
            summary = data.get('summary', '')
            source = data.get('source', 'video_upload')
            
            # Update meeting with transcript and summary
            await self._update_meeting_transcript(meeting_id, transcript, summary)
            
            # Update video processing status only for video upload flow
            if video_id and source == 'video_upload':
                await self._update_video_processing_status(video_id, 'transcribed')
            
            # Log processing step
            await self._log_processing_step(
                meeting_id,
                'transcription',
                'completed',
                {
                    'transcript_length': len(transcript),
                    'summary_length': len(summary),
                    'source': source,
                    'video_id': video_id
                }
            )
            
            logger.info(f"Transcription completed for meeting: {meeting_id} (source: {source})")
            
        except Exception as e:
            logger.error(f"Error handling transcription complete: {str(e)}")
            raise
    
    async def _handle_blog_generation_complete(self, meeting_id: str, data: Dict[str, Any]) -> None:
        """
        Handle blog generation completion
        
        Args:
            meeting_id: Meeting ID
            data: Blog generation data
        """
        try:
            blog_data = {
                'meeting_id': meeting_id,
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'summary': data.get('summary', ''),
                'created_at': data.get('created_at')
            }
            if data.get('blog_id'):
                blog_data['id'] = data.get('blog_id')
            
            # Store blog post
            blog_post = await self._store_blog_post(blog_data)
            
            # Store generated image/poster if provided
            if data.get('image_url') or data.get('poster_url'):
                await self._store_generated_image(
                    meeting_id, 
                    blog_post['id'], 
                    data.get('image_url') or data.get('poster_url'),
                    data.get('image_prompt', ''),
                    data.get('image_type', 'poster')
                )
            
            # Log processing step
            await self._log_processing_step(
                meeting_id,
                'blog_generation',
                'completed',
                {
                    'blog_id': blog_post['id'],
                    'title': blog_data['title'],
                    'image_generated': bool(data.get('image_url') or data.get('poster_url'))
                }
            )
            
            logger.info(f"Blog generation completed for meeting: {meeting_id}")
            
        except Exception as e:
            logger.error(f"Error handling blog generation complete: {str(e)}")
            raise
    
    async def _handle_facebook_post_complete(self, meeting_id: str, data: Dict[str, Any]) -> None:
        """
        Handle Facebook post completion
        
        Args:
            meeting_id: Meeting ID
            data: Facebook post data
        """
        try:
            blog_id = data.get('blog_id')
            facebook_post_id = data.get('facebook_post_id')
            facebook_post_url = data.get('facebook_post_url')
            image_url = data.get('image_url')
            
            # Update blog post with Facebook details
            await self._update_blog_post_facebook(
                blog_id,
                facebook_post_id,
                facebook_post_url
            )
            
            # Update poster/image with Facebook posting info if image was used
            if image_url:
                await self._update_poster_facebook_status(meeting_id, blog_id, image_url)
            
            # Log processing step
            await self._log_processing_step(
                meeting_id,
                'facebook_post',
                'completed',
                {
                    'blog_id': blog_id,
                    'facebook_post_id': facebook_post_id,
                    'facebook_post_url': facebook_post_url,
                    'image_used': bool(image_url)
                }
            )
            
            logger.info(f"Facebook post completed for meeting: {meeting_id}")
            
        except Exception as e:
            logger.error(f"Error handling Facebook post complete: {str(e)}")
            raise
    
    async def _handle_processing_error(self, meeting_id: str, video_id: str = None, error: str = None) -> None:
        """
        Handle processing errors
        
        Args:
            meeting_id: Meeting ID
            video_id: Video ID (optional for meeting ID flow)
            error: Error message
        """
        try:
            # Update video processing status only for video upload flow
            if video_id:
                await self._update_video_processing_status(video_id, 'error')
            
            # Log processing step
            await self._log_processing_step(
                meeting_id,
                'error',
                'failed',
                {
                    'error_message': error,
                    'video_id': video_id
                }
            )
            
            logger.error(f"Processing error for meeting {meeting_id}: {error}")
            
        except Exception as e:
            logger.error(f"Error handling processing error: {str(e)}")
            raise
    
    async def _update_meeting_transcript(self, meeting_id: str, transcript: str, summary: str) -> Dict[str, Any]:
        """Update meeting with transcript and summary"""
        try:
            update_data = {
                'transcript': transcript,
                'summary': summary,
                'transcription_status': 'completed'
            }
            response = self.db_client.table('meetings').update(update_data).eq('id', meeting_id).execute()
            if response.data:
                logger.info(f"Updated meeting transcript: {meeting_id}")
                return response.data[0]
            else:
                raise Exception("Failed to update meeting transcript")
        except Exception as e:
            logger.error(f"Error updating meeting transcript: {str(e)}")
            raise
    
    async def _update_video_processing_status(self, video_id: str, status: str) -> Dict[str, Any]:
        """Update video processing status - Note: meeting_videos table doesn't have processing_status"""
        try:
            # Since meeting_videos table doesn't have processing_status, we'll just log it
            logger.info(f"Video processing status update requested: {video_id} -> {status}")
            return {'status': 'logged'}
        except Exception as e:
            logger.error(f"Error logging video processing status: {str(e)}")
            raise
    
    async def _store_blog_post(self, blog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store generated blog post"""
        try:
            response = self.db_client.table('blog_posts').insert(blog_data).execute()
            if response.data:
                logger.info(f"Stored blog post: {response.data[0]['id']}")
                return response.data[0]
            else:
                raise Exception("Failed to store blog post")
        except Exception as e:
            logger.error(f"Error storing blog post: {str(e)}")
            raise
    
    async def _update_blog_post_facebook(self, blog_id: str, facebook_post_id: str, facebook_post_url: str) -> Dict[str, Any]:
        """Update blog post with Facebook post details"""
        try:
            update_data = {
                'facebook_post_id': facebook_post_id,
                'facebook_post_url': facebook_post_url
            }
            response = self.db_client.table('blog_posts').update(update_data).eq('id', blog_id).execute()
            if response.data:
                logger.info(f"Updated blog post Facebook details: {blog_id}")
                return response.data[0]
            else:
                raise Exception("Failed to update blog post Facebook details")
        except Exception as e:
            logger.error(f"Error updating blog post Facebook details: {str(e)}")
            raise
    
    async def _store_generated_image(self, meeting_id: str, blog_id: str, image_url: str, generation_prompt: str = '', image_type: str = 'poster') -> Dict[str, Any]:
        """Store generated image/poster - Note: posters table doesn't exist in current schema"""
        try:
            # Since posters table doesn't exist, we'll just log it
            logger.info(f"Generated image for meeting {meeting_id}: {image_url}")
            return {'status': 'logged', 'image_url': image_url}
        except Exception as e:
            logger.error(f"Error logging generated image: {str(e)}")
            raise
    
    async def _update_poster_facebook_status(self, meeting_id: str, blog_id: str, image_url: str) -> Dict[str, Any]:
        """Update poster with Facebook posting status - Note: posters table doesn't exist"""
        try:
            # Since posters table doesn't exist, we'll just log it
            logger.info(f"Poster Facebook status update for meeting {meeting_id}: {image_url}")
            return {'status': 'logged'}
        except Exception as e:
            logger.error(f"Error logging poster Facebook status: {str(e)}")
            raise
    
    async def _log_processing_step(self, meeting_id: str, step: str, status: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Log a processing step - Note: processing_logs table doesn't exist in current schema"""
        try:
            # Since processing_logs table doesn't exist, we'll just log it
            logger.info(f"Processing step: {meeting_id} - {step} - {status} - {details}")
            return {'status': 'logged'}
        except Exception as e:
            logger.error(f"Error logging processing step: {str(e)}")
            raise 