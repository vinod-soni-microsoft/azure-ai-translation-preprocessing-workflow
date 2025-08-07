#!/usr/bin/env python3
"""
Complete integration test with file uploads
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_file_upload():
    """Test file upload and processing."""
    print("🧪 Testing file upload and processing...")
    
    # Test valid DOCX file
    if Path("uploads/sample_valid.docx").exists():
        print("\n📄 Testing valid DOCX file upload...")
        with open("uploads/sample_valid.docx", "rb") as f:
            files = {"file": ("sample_valid.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('success', False)}")
                print(f"📝 Content found: {result.get('content_analysis', {}).get('has_translatable_content', False)}")
                if result.get('download_url'):
                    print(f"⬇️  Download: {BASE_URL}{result['download_url']}")
                print(f"📊 Analysis: {json.dumps(result.get('content_analysis', {}), indent=2)}")
            else:
                print(f"❌ Failed: {response.text}")
    
    # Test validation endpoint
    if Path("uploads/fake_docx.docx").exists():
        print("\n🔍 Testing fake DOCX validation...")
        with open("uploads/fake_docx.docx", "rb") as f:
            files = {"file": ("fake_docx.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(f"{BASE_URL}/validate", files=files)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Validation result: {result.get('is_valid', False)}")
                print(f"📝 Message: {result.get('message', 'No message')}")
            else:
                print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    print("🚀 Running complete integration test...")
    try:
        test_file_upload()
        print("\n✅ Integration test completed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
