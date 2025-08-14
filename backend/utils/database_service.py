"""
Database Service for Blog Automation System

This module handles all database operations and queries including:
- Database connection testing
- Common database operations
- Query building and execution
- Error handling

Input Types:
- table_name: String - Name of database table
- data: Dict[str, Any] - Data to insert/update
- filters: Dict[str, Any] - Filter conditions
- limit: Integer - Number of records to return
- offset: Integer - Number of records to skip

Output Types:
- success: Boolean
- data: List[Dict[str, Any]] or Dict[str, Any]
- count: Integer
- error: String (if operation fails)

Author: Your Name
Date: 2024
"""

import logging
from typing import Dict, Any, List, Optional

from db import get_db_client

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self):
        """Initialize database service"""
        self.db_client = get_db_client()
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Simple test query to verify connection
            response = self.db_client.table('meetings').select('count', count='exact').execute()
            return response.data is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert a record into the specified table
        
        Args:
            table_name: Name of the table
            data: Data to insert
            
        Returns:
            Optional[Dict[str, Any]]: Inserted record or None if failed
        """
        try:
            response = self.db_client.table(table_name).insert(data).execute()
            if response.data:
                logger.info(f"Inserted record into {table_name}: {response.data[0].get('id', 'unknown')}")
                return response.data[0]
            else:
                logger.error(f"Failed to insert record into {table_name}")
                return None
        except Exception as e:
            logger.error(f"Error inserting record into {table_name}: {str(e)}")
            return None
    
    def update_record(self, table_name: str, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a record in the specified table
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to update
            data: Data to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated record or None if failed
        """
        try:
            response = self.db_client.table(table_name).update(data).eq('id', record_id).execute()
            if response.data:
                logger.info(f"Updated record in {table_name}: {record_id}")
                return response.data[0]
            else:
                logger.error(f"Failed to update record in {table_name}: {record_id}")
                return None
        except Exception as e:
            logger.error(f"Error updating record in {table_name}: {str(e)}")
            return None
    
    def get_record_by_id(self, table_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a record by ID from the specified table
        
        Args:
            table_name: Name of the table
            record_id: ID of the record
            
        Returns:
            Optional[Dict[str, Any]]: Record or None if not found
        """
        try:
            response = self.db_client.table(table_name).select('*').eq('id', record_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting record from {table_name}: {str(e)}")
            return None
    
    def get_records(self, table_name: str, filters: Dict[str, Any] = None, 
                   limit: int = None, offset: int = None, order_by: str = None) -> List[Dict[str, Any]]:
        """
        Get records from the specified table with optional filtering and pagination
        
        Args:
            table_name: Name of the table
            filters: Filter conditions
            limit: Number of records to return
            offset: Number of records to skip
            order_by: Order by clause
            
        Returns:
            List[Dict[str, Any]]: List of records
        """
        try:
            query = self.db_client.table(table_name).select('*')
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Apply ordering
            if order_by:
                if order_by.startswith('-'):
                    query = query.order(order_by[1:], desc=True)
                else:
                    query = query.order(order_by)
            
            # Apply pagination
            if limit is not None and offset is not None:
                query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting records from {table_name}: {str(e)}")
            return []
    
    def get_count(self, table_name: str, filters: Dict[str, Any] = None) -> int:
        """
        Get count of records in the specified table with optional filtering
        
        Args:
            table_name: Name of the table
            filters: Filter conditions
            
        Returns:
            int: Count of records
        """
        try:
            query = self.db_client.table(table_name).select('count', count='exact')
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.count or 0
            
        except Exception as e:
            logger.error(f"Error getting count from {table_name}: {str(e)}")
            return 0
    
    def delete_record(self, table_name: str, record_id: str) -> bool:
        """
        Delete a record from the specified table
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.db_client.table(table_name).delete().eq('id', record_id).execute()
            if response.data:
                logger.info(f"Deleted record from {table_name}: {record_id}")
                return True
            else:
                logger.error(f"Failed to delete record from {table_name}: {record_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting record from {table_name}: {str(e)}")
            return False
    
    def execute_custom_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        try:
            # Note: This is a simplified implementation
            # In a real application, you might want to use raw SQL execution
            # For Supabase, you typically use the query builder instead
            logger.warning("Custom query execution not implemented for Supabase")
            return []
        except Exception as e:
            logger.error(f"Error executing custom query: {str(e)}")
            return [] 