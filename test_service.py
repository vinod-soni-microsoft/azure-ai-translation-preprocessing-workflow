#!/usr/bin/env python3
"""
Test script for the Document Processing Service
Tests both positive and negative scenarios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.document_service import DocumentService
from pathlib import Path
import json

def print_separator(title):
    """Print a separator with title."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(test_name, result):
    """Print test result in a formatted way."""
    print(f"\n🧪 TEST: {test_name}")
    print("-" * 40)
    
    if isinstance(result, dict):
        if 'success' in result:
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            print(f"Status: {status}")
        
        # Print key information
        for key, value in result.items():
            if key in ['validation', 'content_analysis', 'conversion', 'errors']:
                print(f"{key.title()}: {json.dumps(value, indent=2)}")
            elif key not in ['metadata', 'input_file']:
                print(f"{key}: {value}")
    else:
        print(f"Result: {result}")

def test_positive_scenarios():
    """Test positive scenarios with valid files."""
    print_separator("POSITIVE TEST SCENARIOS")
    
    service = DocumentService("logs")
    
    # Test 1: Valid DOCX file
    test_file = "uploads/sample_valid.docx"
    if Path(test_file).exists():
        print_result("Valid DOCX Processing", 
                    service.process_document(test_file, "converted"))
    else:
        print(f"❌ Test file not found: {test_file}")
    
    # Test 2: Validation only
    if Path(test_file).exists():
        print_result("DOCX Validation Only", 
                    service.validate_document_only(test_file))

def test_negative_scenarios():
    """Test negative scenarios with invalid files."""
    print_separator("NEGATIVE TEST SCENARIOS")
    
    service = DocumentService("logs")
    
    # Test 1: Fake DOCX file
    test_file = "uploads/fake_docx.docx"
    if Path(test_file).exists():
        print_result("Fake DOCX File", 
                    service.process_document(test_file, "converted"))
    
    # Test 2: Empty/Invalid DOCX
    test_file = "uploads/empty_invalid.docx"
    if Path(test_file).exists():
        print_result("Empty Invalid DOCX", 
                    service.process_document(test_file, "converted"))
    
    # Test 3: Non-existent file
    print_result("Non-existent File", 
                service.process_document("uploads/nonexistent.docx", "converted"))

def test_conversion_scenarios():
    """Test file conversion scenarios."""
    print_separator("CONVERSION TEST SCENARIOS")
    
    service = DocumentService("logs")
    
    # Test 1: Text file conversion
    test_file = "uploads/sample.txt"
    if Path(test_file).exists():
        print_result("Text File Conversion", 
                    service.process_document(test_file, "converted"))
    
    # Test supported formats
    print_result("Supported Formats", 
                service.get_supported_formats())

def test_service_features():
    """Test additional service features."""
    print_separator("SERVICE FEATURES TEST")
    
    service = DocumentService("logs")
    
    # Test processing summary
    print_result("Processing Summary (Last 24 hours)", 
                service.get_processing_summary(24))

def main():
    """Run all tests."""
    print("🚀 Starting Document Processing Service Tests")
    
    # Create necessary directories
    os.makedirs("converted", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    try:
        test_positive_scenarios()
        test_negative_scenarios()
        test_conversion_scenarios()
        test_service_features()
        
        print_separator("TEST SUMMARY")
        print("✅ All tests completed!")
        print("📁 Check the 'logs' directory for detailed operation logs")
        print("📁 Check the 'converted' directory for converted files")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
