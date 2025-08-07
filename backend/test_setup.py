#!/usr/bin/env python3
"""
Test script to verify the backend setup
Run this to check if everything is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_environment():
    """Test if environment variables are set"""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY',
        'ASSEMBLY_AI_API_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_database_connection():
    """Test database connection"""
    try:
        from db import get_db_client, test_db_connection
        
        client = get_db_client()
        if test_db_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

def test_imports():
    """Test if all modules can be imported"""
    try:
        from utils.upload_service import UploadService
        from utils.webhook_service import WebhookService
        from utils.meeting_service import MeetingService
        from utils.video_processor import VideoProcessor
        from utils.database_service import DatabaseService
        from utils.validation_service import ValidationService
        from utils.file_manager import FileManager
        
        print("✅ All utility modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def main():
    print("🔍 Testing Backend Setup")
    print("=" * 40)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Database Connection", test_database_connection),
        ("Module Imports", test_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your backend is ready.")
        print("\n📝 Next steps:")
        print("1. Create your .env file with real credentials")
        print("2. Set up Supabase tables (coordinate with your team)")
        print("3. Run: python main.py")
        print("4. Test the API endpoints")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 