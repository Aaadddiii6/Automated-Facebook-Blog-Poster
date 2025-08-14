"""
Database connection module for Blog Automation System

This module is solely responsible for:
- Initializing the Supabase database client
- Providing database connection objects
- No business logic or SQL queries should be here

Author: Your Name
Date: 2024
"""

import os
from supabase import create_client, Client
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager"""
    
    _instance: Optional['DatabaseConnection'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern to ensure single database connection"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection"""
        if not self._client:
            self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Supabase client with environment variables"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables"
                )
            
            self._client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        if not self._client:
            self._initialize_client()
        return self._client
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Simple test query to verify connection
            response = self._client.table('meetings').select('count', count='exact').execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def close_connection(self) -> None:
        """Close database connection (if needed)"""
        # Supabase client doesn't require explicit closing
        # This method is included for consistency
        logger.info("Database connection closed")
        self._client = None

# Global database connection instance
db_connection = DatabaseConnection()

def get_db_client() -> Client:
    """
    Get database client instance
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        Exception: If database connection fails
    """
    return db_connection.get_client()

def test_db_connection() -> bool:
    """
    Test database connection
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    return db_connection.test_connection() 