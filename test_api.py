#!/usr/bin/env python3
"""
API Test script for the Document Processing Service
Tests the REST API endpoints with various scenarios
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_separator(title):
    """Print a separator with title."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_api_result(test_name, response):
    """Print API test result."""
    print(f"\n🌐 API TEST: {test_name}")
    print("-" * 40)
    print(f"Status Code: {response.status_code}")
    
    try:
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Response: {response.text[:500]}...")
    except:
        print(f"Response: {response.text[:200]}...")

def test_service_endpoints():
    """Test basic service endpoints."""
    print_separator("SERVICE ENDPOINTS TEST")
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print_api_result("Root Endpoint", response)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Make sure it's running on http://localhost:8000")
        return False
    
    # Test health endpoint
    response = requests.get(f"{BASE_URL}/health")
    print_api_result("Health Check", response)
    
    # Test supported formats
    response = requests.get(f"{BASE_URL}/formats")
    print_api_result("Supported Formats", response)
    
    return True

def test_file_validation():
    """Test file validation API."""
    print_separator("FILE VALIDATION API TEST")
    
    # Test valid DOCX file
    if Path("../uploads/sample_valid.docx").exists():
        with open("../uploads/sample_valid.docx", "rb") as f:
            files = {"file": ("sample_valid.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{BASE_URL}/validate", files=files)
            print_api_result("Valid DOCX Validation", response)
    
    # Test invalid DOCX file
    if Path("../uploads/fake_docx.docx").exists():
        with open("../uploads/fake_docx.docx", "rb") as f:
            files = {"file": ("fake_docx.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{BASE_URL}/validate", files=files)
            print_api_result("Invalid DOCX Validation", response)

def test_file_processing():
    """Test file processing API."""
    print_separator("FILE PROCESSING API TEST")
    
    # Test valid DOCX processing
    if Path("../uploads/sample_valid.docx").exists():
        with open("../uploads/sample_valid.docx", "rb") as f:
            files = {"file": ("sample_valid.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            print_api_result("Valid DOCX Processing", response)
    
    # Test text file processing (should fail without LibreOffice)
    if Path("../uploads/sample.txt").exists():
        with open("../uploads/sample.txt", "rb") as f:
            files = {"file": ("sample.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            print_api_result("Text File Processing", response)

def test_summary_endpoint():
    """Test processing summary endpoint."""
    print_separator("SUMMARY ENDPOINT TEST")
    
    response = requests.get(f"{BASE_URL}/summary?hours=1")
    print_api_result("Processing Summary", response)

def main():
    """Run all API tests."""
    print("🚀 Starting Document Processing Service API Tests")
    print("📡 Testing service at: http://localhost:8000")
    
    # Wait a moment for service to be ready
    time.sleep(2)
    
    try:
        if not test_service_endpoints():
            return
        
        test_file_validation()
        test_file_processing()
        test_summary_endpoint()
        
        print_separator("API TEST SUMMARY")
        print("✅ All API tests completed!")
        print("🌐 Service is running at: http://localhost:8000")
        print("📖 API Documentation available at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ API test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
