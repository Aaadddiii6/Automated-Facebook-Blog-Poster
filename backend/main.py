"""
Main Flask application for Video-to-Blog Automation System

This module contains:
- Flask application initialization
- API route definitions (controllers)
- Error handlers
- No business logic (delegated to utils/)

Author: Your Name
Date: 2024
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
import signal
import sys

# Import business logic from utils
from utils.upload_service import UploadService
from utils.webhook_service import WebhookService
from utils.meeting_service import MeetingService
from utils.meeting_processor_service import MeetingProcessorService
from utils.video_processor import VideoProcessor
from utils.database_service import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Security and middleware setup
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    
    # Enable CORS
    CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))
    
    # Initialize services
    upload_service = UploadService()
    webhook_service = WebhookService()
    meeting_service = MeetingService()
    meeting_processor_service = MeetingProcessorService()
    video_processor = VideoProcessor()
    db_service = DatabaseService()
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            db_healthy = db_service.test_connection()
            
            return jsonify({
                'status': 'healthy' if db_healthy else 'degraded',
                'database': 'connected' if db_healthy else 'disconnected',
                'timestamp': '2024-01-01T00:00:00Z',
                'version': '1.0.0'
            }), 200 if db_healthy else 503
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': '2024-01-01T00:00:00Z',
                'version': '1.0.0'
            }), 503
    
    # Video Upload Routes
    @app.route('/api/upload', methods=['POST'])
    def upload_video():
        """
        Upload video file endpoint
        
        Expected form data:
        - file: Video file
        - title: Meeting title (optional)
        - description: Meeting description (optional)
        - organization_id: Organization ID (optional)
        
        Returns:
        - 200: Upload successful
        - 400: Invalid request
        - 413: File too large
        - 500: Server error
        """
        # Process the upload asynchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result, status_code = loop.run_until_complete(
                upload_service.handle_video_upload(request)
            )
            return result, status_code
        finally:
            loop.close()
    
    # Meeting ID Processing Routes
    @app.route('/api/process-meeting', methods=['POST'])
    def process_meeting():
        """
        Process meeting ID to fetch transcript from Supabase
        
        Expected JSON payload:
        {
            "meeting_id": "uuid",
            "organization_id": "uuid"
        }
        
        Returns:
        - 200: Processing started successfully
        - 400: Invalid request or meeting ID
        - 404: Meeting not found in Supabase
        - 500: Server error
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            meeting_id = data.get('meeting_id')
            organization_id = data.get('organization_id')
            
            if not meeting_id or not organization_id:
                return jsonify({'error': 'meeting_id and organization_id are required'}), 400
            
            # Process the meeting ID asynchronously
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result, status_code = loop.run_until_complete(
                    meeting_processor_service.process_meeting_id(meeting_id, organization_id)
                )
                return jsonify(result), status_code
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error processing meeting: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/upload/status/<meeting_id>', methods=['GET'])
    def get_processing_status(meeting_id):
        """
        Get processing status for a meeting
        
        Args:
        - meeting_id: UUID of the meeting
        
        Returns:
        - 200: Status information
        - 404: Meeting not found
        - 500: Server error
        """
        return meeting_service.get_processing_status(meeting_id)
    
    # Webhook Routes
    @app.route('/api/webhook', methods=['POST'])
    def webhook_handler():
        """
        Universal Make.com webhook handler (handles both flows)
        
        Expected JSON payload:
        {
            "meeting_id": "uuid",
            "video_id": "uuid", 
            "step": "transcription_complete|blog_generation_complete|facebook_post_complete|processing_error",
            "data": {...},
            "error": "error message" (optional)
        }
        
        Returns:
        - 200: Webhook processed successfully
        - 400: Invalid payload
        - 500: Server error
        """
        return webhook_service.handle_webhook(request)
    
    @app.route('/api/webhook/video-upload', methods=['POST'])
    def video_upload_webhook_handler():
        """
        Video Upload Flow webhook handler
        
        This endpoint is specifically for the video upload flow:
        1. Video uploaded to Cloudinary
        2. Assembly AI processes video
        3. OpenAI generates blog and images
        4. Facebook posting
        
        Expected JSON payload:
        {
            "meeting_id": "uuid",
            "video_id": "uuid", 
            "step": "transcription_complete|blog_generation_complete|facebook_post_complete|processing_error",
            "data": {...},
            "error": "error message" (optional)
        }
        
        Returns:
        - 200: Webhook processed successfully
        - 400: Invalid payload
        - 500: Server error
        """
        return webhook_service.handle_webhook(request)
    
    @app.route('/api/webhook/meeting-id', methods=['POST'])
    def meeting_id_webhook_handler():
        """
        Meeting ID Flow webhook handler
        
        This endpoint is specifically for the meeting ID flow:
        1. Transcript fetched from Supabase
        2. OpenAI generates blog and images
        3. Facebook posting
        
        Expected JSON payload:
        {
            "meeting_id": "uuid",
            "step": "transcription_complete|blog_generation_complete|facebook_post_complete|processing_error",
            "data": {
                "transcript": "...",
                "summary": "...",
                "source": "supabase",
                "supabase_meeting_id": "uuid"
            },
            "error": "error message" (optional)
        }
        
        Returns:
        - 200: Webhook processed successfully
        - 400: Invalid payload
        - 500: Server error
        """
        return webhook_service.handle_webhook(request)
    
    # Meeting Routes
    @app.route('/api/meetings', methods=['GET'])
    def get_meetings():
        """
        Get list of meetings
        
        Query parameters:
        - organization_id: Filter by organization (optional)
        - limit: Number of records to return (default: 10)
        - offset: Number of records to skip (default: 0)
        
        Returns:
        - 200: List of meetings
        - 500: Server error
        """
        organization_id = request.args.get('organization_id')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        return meeting_service.get_meetings(organization_id, limit, offset)
    
    @app.route('/api/meetings/<meeting_id>', methods=['GET'])
    def get_meeting(meeting_id):
        """
        Get meeting details
        
        Args:
        - meeting_id: UUID of the meeting
        
        Returns:
        - 200: Meeting details
        - 404: Meeting not found
        - 500: Server error
        """
        return meeting_service.get_meeting(meeting_id)
    
    # Video Routes
    @app.route('/api/videos/<video_id>/info', methods=['GET'])
    def get_video_info(video_id):
        """
        Get video file information
        
        Args:
        - video_id: UUID of the video file
        
        Returns:
        - 200: Video information
        - 404: Video not found
        - 500: Server error
        """
        return video_processor.get_video_info_by_id(video_id)
    
    # Video file serving endpoint (for Make.com and Assembly AI)
    @app.route('/api/videos/<video_id>/file', methods=['GET'])
    def serve_video_file(video_id):
        """
        Serve video file for external access (Make.com, Assembly AI)
        
        Args:
        - video_id: UUID of the video file
        
        Returns:
        - 200: Video file stream
        - 404: Video not found
        - 500: Server error
        """
        try:
            # Get video info from database
            response = video_processor.get_video_info_by_id(video_id)
            
            if response[1] != 200:  # Check status code
                return response
            
            video_data = response[0].json
            file_path = video_data.get('file_path')
            
            if not file_path or not os.path.exists(file_path):
                return jsonify({'error': 'Video file not found'}), 404
            
            # Serve the video file
            return send_file(
                file_path,
                mimetype='video/mp4',
                as_attachment=False,
                download_name=os.path.basename(file_path)
            )
            
        except Exception as e:
            logger.error(f"Error serving video file: {str(e)}")
            return jsonify({'error': 'Failed to serve video file'}), 500
    
    # Frontend Routes
    @app.route('/', methods=['GET'])
    def serve_upload_page():
        """Serve the video upload page"""
        return send_from_directory('../frontend', 'upload.html')
    
    @app.route('/dashboard', methods=['GET'])
    def serve_dashboard():
        """Serve the processing dashboard"""
        return send_from_directory('../frontend', 'dashboard.html')
    
    # Error Handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large'}), 413
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Shutting down gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the application
    app = create_app()
    
    # Get port from environment or default to 3000
    port = int(os.getenv('PORT', 3000))
    
    logger.info(f"Starting Flask application on port {port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development'
    ) 