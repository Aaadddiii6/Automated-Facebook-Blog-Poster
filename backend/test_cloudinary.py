#!/usr/bin/env python3
"""
Test script to verify Cloudinary credentials
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_cloudinary_credentials():
    """Test Cloudinary credentials"""
    
    # Get credentials from environment
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    print("=== Cloudinary Credentials Test ===")
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key[:5]}..." if api_key else "API Key: Not set")
    print(f"API Secret: {api_secret[:5]}..." if api_secret else "API Secret: Not set")
    
    # Check if all credentials are set
    if not all([cloud_name, api_key, api_secret]):
        print("\n❌ ERROR: Missing Cloudinary credentials!")
        print("Please check your .env file and ensure all Cloudinary variables are set.")
        return False
    
    # Test Cloudinary connection
    try:
        import cloudinary
        import cloudinary.api
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Test API call
        result = cloudinary.api.ping()
        print(f"\n✅ SUCCESS: Cloudinary connection working!")
        print(f"Response: {result}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Cloudinary connection failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_cloudinary_credentials()
    sys.exit(0 if success else 1) 