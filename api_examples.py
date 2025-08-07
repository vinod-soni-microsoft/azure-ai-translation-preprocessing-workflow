#!/usr/bin/env python3
"""
Sample API usage examples for the Document Processing Service
This script demonstrates how to use the API programmatically
"""

import requests
import json
import time
from pathlib import Path
import os

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class DocumentProcessingClient:
    """Client for the Document Processing Service API."""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self):
        """Check if the service is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=TIMEOUT)
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, {"error": str(e)}
    
    def get_supported_formats(self):
        """Get supported file formats."""
        try:
            response = self.session.get(f"{self.base_url}/formats", timeout=TIMEOUT)
            response.raise_for_status()
            return True, response.json()
        except Exception as e:
            return False, {"error": str(e)}
    
    def validate_document(self, file_path):
        """Validate a document without full processing."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f)}
                response = self.session.post(
                    f"{self.base_url}/validate", 
                    files=files, 
                    timeout=TIMEOUT
                )
                response.raise_for_status()
                return True, response.json()
        except Exception as e:
            return False, {"error": str(e)}
    
    def process_document(self, file_path, keep_original=True):
        """Process a document through the complete pipeline."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f)}
                data = {'keep_original': keep_original}
                response = self.session.post(
                    f"{self.base_url}/upload", 
                    files=files, 
                    data=data,
                    timeout=TIMEOUT
                )
                response.raise_for_status()
                return True, response.json()
        except Exception as e:
            return False, {"error": str(e)}
    
    def download_file(self, filename, output_path=None):
        """Download a processed file."""
        try:
            response = self.session.get(
                f"{self.base_url}/download/{filename}", 
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            if output_path is None:
                output_path = filename
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True, {"message": f"File downloaded to {output_path}"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def get_processing_summary(self, hours=24):
        """Get processing summary for the last N hours."""
        try:
            response = self.session.get(
                f"{self.base_url}/summary", 
                params={'hours': hours},
                timeout=TIMEOUT
            )
            response.raise_for_status()
            return True, response.json()
        except Exception as e:
            return False, {"error": str(e)}

def print_result(operation, success, result):
    """Print operation result in a formatted way."""
    print(f"\n{'='*60}")
    print(f"🔧 OPERATION: {operation}")
    print(f"{'='*60}")
    
    if success:
        print("✅ SUCCESS")
        print(json.dumps(result, indent=2))
    else:
        print("❌ FAILED")
        print(json.dumps(result, indent=2))

def example_basic_usage():
    """Example of basic API usage."""
    print("🚀 Basic API Usage Examples")
    
    client = DocumentProcessingClient()
    
    # 1. Health check
    success, result = client.health_check()
    print_result("Health Check", success, result)
    
    if not success:
        print("❌ Service is not available. Make sure it's running at http://localhost:8000")
        return
    
    # 2. Get supported formats
    success, result = client.get_supported_formats()
    print_result("Get Supported Formats", success, result)
    
    # 3. Process a valid document (if available)
    test_file = "uploads/sample_valid.docx"
    if Path(test_file).exists():
        success, result = client.validate_document(test_file)
        print_result("Validate Document", success, result)
        
        success, result = client.process_document(test_file)
        print_result("Process Document", success, result)
        
        if success and result.get('download_url'):
            # Extract filename from download URL
            filename = result['download_url'].split('/')[-1]
            success, download_result = client.download_file(filename, f"downloaded_{filename}")
            print_result("Download Processed File", success, download_result)
    
    # 4. Get processing summary
    success, result = client.get_processing_summary(hours=1)
    print_result("Processing Summary", success, result)

def example_batch_processing():
    """Example of batch processing multiple files."""
    print("\n🔄 Batch Processing Example")
    
    client = DocumentProcessingClient()
    
    # Check if service is available
    success, _ = client.health_check()
    if not success:
        print("❌ Service not available")
        return
    
    # Process all files in uploads directory
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ No uploads directory found")
        return
    
    results = []
    
    for file_path in uploads_dir.iterdir():
        if file_path.is_file():
            print(f"\n📄 Processing: {file_path.name}")
            
            # Validate first
            success, result = client.validate_document(str(file_path))
            
            if success and result.get('is_valid'):
                # Process if valid
                success, process_result = client.process_document(str(file_path))
                results.append({
                    'file': file_path.name,
                    'success': success,
                    'result': process_result
                })
                
                if success:
                    print(f"   ✅ Processed successfully")
                    analysis = process_result.get('content_analysis', {}).get('analysis', {})
                    print(f"   📊 Words: {analysis.get('total_words', 0)}")
                    print(f"   🌐 Translatable: {analysis.get('has_translatable_text', False)}")
                else:
                    print(f"   ❌ Processing failed: {process_result.get('error', 'Unknown error')}")
            else:
                print(f"   ⚠️  Validation failed: {result.get('message', 'Unknown error')}")
    
    # Summary
    print(f"\n📊 Batch Processing Summary:")
    print(f"   Total files: {len(results)}")
    print(f"   Successful: {sum(1 for r in results if r['success'])}")
    print(f"   Failed: {sum(1 for r in results if not r['success'])}")

def example_error_handling():
    """Example of proper error handling."""
    print("\n🛡️ Error Handling Examples")
    
    client = DocumentProcessingClient()
    
    # Test with non-existent file
    success, result = client.validate_document("nonexistent.docx")
    print_result("Validate Non-existent File", success, result)
    
    # Test with invalid service URL
    invalid_client = DocumentProcessingClient("http://localhost:9999")
    success, result = invalid_client.health_check()
    print_result("Connect to Invalid Service", success, result)

def example_custom_processing():
    """Example of custom processing logic."""
    print("\n⚙️ Custom Processing Example")
    
    client = DocumentProcessingClient()
    
    # Custom processing workflow
    def analyze_document_content(file_path):
        """Custom function to analyze document content."""
        success, result = client.process_document(file_path)
        
        if not success:
            return {"error": "Processing failed", "details": result}
        
        if not result.get('success'):
            return {"error": "Document processing unsuccessful", "details": result}
        
        # Extract key metrics
        analysis = result.get('content_analysis', {}).get('analysis', {})
        
        return {
            "file": Path(file_path).name,
            "valid_docx": result.get('validation', {}).get('is_valid_docx', False),
            "has_content": analysis.get('has_translatable_text', False),
            "word_count": analysis.get('total_words', 0),
            "paragraph_count": analysis.get('paragraph_count', 0),
            "table_count": analysis.get('table_count', 0),
            "language_hints": analysis.get('language_hints', []),
            "conversion_needed": result.get('conversion', {}).get('needed', False),
            "processing_successful": result.get('success', False)
        }
    
    # Test with available files
    test_files = ["uploads/sample_valid.docx", "uploads/fake_docx.docx", "uploads/sample.txt"]
    
    for file_path in test_files:
        if Path(file_path).exists():
            analysis = analyze_document_content(file_path)
            print_result(f"Custom Analysis: {Path(file_path).name}", True, analysis)

def example_monitoring():
    """Example of service monitoring."""
    print("\n📊 Service Monitoring Example")
    
    client = DocumentProcessingClient()
    
    # Monitor service over time
    def monitor_service(duration_seconds=30, interval_seconds=5):
        """Monitor service health and performance."""
        print(f"🔍 Monitoring service for {duration_seconds} seconds...")
        
        start_time = time.time()
        checks = []
        
        while time.time() - start_time < duration_seconds:
            check_time = time.time()
            success, result = client.health_check()
            
            check_result = {
                "timestamp": time.strftime("%H:%M:%S"),
                "healthy": success,
                "response_time": time.time() - check_time,
                "libreoffice_available": result.get('libreoffice_available', False) if success else False
            }
            
            checks.append(check_result)
            print(f"   {check_result['timestamp']}: {'✅' if success else '❌'} "
                  f"({check_result['response_time']:.3f}s)")
            
            if time.time() - start_time < duration_seconds:
                time.sleep(interval_seconds)
        
        # Summary
        healthy_count = sum(1 for c in checks if c['healthy'])
        avg_response_time = sum(c['response_time'] for c in checks) / len(checks)
        
        print(f"\n📊 Monitoring Summary:")
        print(f"   Total checks: {len(checks)}")
        print(f"   Healthy: {healthy_count}/{len(checks)} ({healthy_count/len(checks)*100:.1f}%)")
        print(f"   Average response time: {avg_response_time:.3f}s")
    
    # Run short monitoring session
    monitor_service(duration_seconds=15, interval_seconds=3)

def main():
    """Main function to run all examples."""
    print("🎯 Document Processing Service - API Usage Examples")
    print("="*60)
    
    try:
        # Run examples
        example_basic_usage()
        example_batch_processing()
        example_error_handling()
        example_custom_processing()
        example_monitoring()
        
        print("\n✅ All examples completed!")
        print("\n📖 For more information, see:")
        print("   • COMPLETE_GUIDE.md - Full documentation")
        print("   • http://localhost:8000/docs - Interactive API docs")
        
    except KeyboardInterrupt:
        print("\n\n👋 Examples stopped by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
