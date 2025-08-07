#!/usr/bin/env python3
"""
Test script for Azure AI Translate compatibility analysis.
Demonstrates the enhanced translatable text detection capabilities.
"""

import requests
import json
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_FILES = [
    "uploads/sample_valid.docx",
    "uploads/fake_docx.docx", 
    "uploads/empty_invalid.docx"
]

def test_azure_translate_analysis():
    """Test the Azure AI Translate analysis endpoint."""
    print("=" * 60)
    print("AZURE AI TRANSLATE COMPATIBILITY ANALYSIS TEST")
    print("=" * 60)
    
    for file_path in TEST_FILES:
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"\n🔍 Analyzing: {file_path}")
        print("-" * 40)
        
        try:
            # Test the Azure AI Translate analysis endpoint
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                response = requests.post(f"{BASE_URL}/azure-translate-analysis", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print_azure_analysis(result)
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def print_azure_analysis(result):
    """Print Azure AI Translate analysis results in a readable format."""
    print(f"📁 File: {result.get('file_path', 'Unknown')}")
    print(f"✅ Format Valid: {result.get('format_valid', False)}")
    
    azure_analysis = result.get('azure_analysis', {})
    
    if 'error' in azure_analysis:
        print(f"❌ Analysis Error: {azure_analysis['error']}")
        return
    
    # Main readiness status
    ready = azure_analysis.get('ready_for_translation', False)
    readiness_score = azure_analysis.get('readiness_score', '0%')
    
    print(f"🚀 Azure AI Translate Ready: {'✅ YES' if ready else '❌ NO'}")
    print(f"📊 Readiness Score: {readiness_score}")
    
    # Content metrics
    translatable_words = azure_analysis.get('translatable_words', 0)
    detected_languages = azure_analysis.get('detected_languages', [])
    content_types = azure_analysis.get('content_types', [])
    
    print(f"📝 Translatable Words: {translatable_words}")
    print(f"🌍 Detected Languages: {', '.join(detected_languages) if detected_languages else 'None'}")
    print(f"📋 Content Types: {', '.join(content_types) if content_types else 'None'}")
    
    # Recommendations
    recommendations = azure_analysis.get('key_recommendations', [])
    if recommendations:
        print("💡 Key Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    # Azure compatibility
    azure_compatible = azure_analysis.get('azure_compatibility', False)
    print(f"🔧 Azure Service Compatible: {'✅ YES' if azure_compatible else '❌ NO'}")

def test_comparison_with_legacy():
    """Compare Azure AI analysis with legacy analysis."""
    print("\n" + "=" * 60)
    print("COMPARISON: AZURE AI vs LEGACY ANALYSIS")
    print("=" * 60)
    
    test_file = "uploads/sample_valid.docx"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    try:
        # Test legacy validation endpoint
        with open(test_file, 'rb') as f:
            files = {'file': (Path(test_file).name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            legacy_response = requests.post(f"{BASE_URL}/validate", files=files)
        
        # Test Azure AI analysis endpoint
        with open(test_file, 'rb') as f:
            files = {'file': (Path(test_file).name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            azure_response = requests.post(f"{BASE_URL}/azure-translate-analysis", files=files)
        
        if legacy_response.status_code == 200 and azure_response.status_code == 200:
            legacy_result = legacy_response.json()
            azure_result = azure_response.json()
            
            print("📊 LEGACY ANALYSIS:")
            legacy_content = legacy_result.get('content_analysis', {})
            print(f"   Has Translatable Text: {legacy_content.get('has_translatable_text', False)}")
            print(f"   Total Words: {legacy_content.get('total_words', 0)}")
            print(f"   Estimated Translatable Words: {legacy_content.get('estimated_translatable_words', 0)}")
            
            print("\n🚀 AZURE AI ANALYSIS:")
            azure_analysis = azure_result.get('azure_analysis', {})
            print(f"   Ready for Translation: {azure_analysis.get('ready_for_translation', False)}")
            print(f"   Readiness Score: {azure_analysis.get('readiness_score', '0%')}")
            print(f"   Translatable Words: {azure_analysis.get('translatable_words', 0)}")
            print(f"   Detected Languages: {', '.join(azure_analysis.get('detected_languages', []))}")
            print(f"   Azure Compatible: {azure_analysis.get('azure_compatibility', False)}")
            
            print("\n🔍 KEY DIFFERENCES:")
            print("   • Azure AI analysis provides language detection")
            print("   • Azure AI analysis includes readiness scoring")
            print("   • Azure AI analysis validates Azure service compatibility")
            print("   • Azure AI analysis provides specific recommendations")
            print("   • Azure AI analysis considers segmentation optimization")
            
        else:
            print("❌ Failed to get comparison data")
            
    except Exception as e:
        print(f"❌ Comparison error: {e}")

def show_azure_ai_standards():
    """Display Azure AI Translate standards implemented."""
    print("\n" + "=" * 60)
    print("AZURE AI TRANSLATE STANDARDS IMPLEMENTED")
    print("=" * 60)
    
    standards = [
        "✅ DOCX Format Validation - Ensures Strict Open XML compliance",
        "✅ Language Detection - Identifies document languages automatically", 
        "✅ Content Segmentation - Optimizes text segments for translation",
        "✅ Translatable Text Filtering - Excludes non-translatable content",
        "✅ Character/Word Counting - Accurate metrics for translation planning",
        "✅ Format Preservation Analysis - Ensures formatting compatibility",
        "✅ Multi-language Detection - Handles mixed-language documents",
        "✅ Readiness Scoring - Quantifies translation preparation",
        "✅ Azure Service Compatibility - Validates service requirements",
        "✅ Segmentation Optimization - Respects Azure size limits (5000 chars)",
        "✅ Recommendation Engine - Provides actionable improvement suggestions"
    ]
    
    for standard in standards:
        print(f"   {standard}")
    
    print("\n🎯 BENEFITS FOR AZURE AI TRANSLATE:")
    benefits = [
        "• Improved translation quality through better content preparation",
        "• Reduced translation errors via format validation",
        "• Optimized API usage through intelligent segmentation",
        "• Better cost management via accurate word counting", 
        "• Enhanced workflow through readiness validation",
        "• Preserved document formatting in translated output"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")

def main():
    """Main test execution."""
    print("🚀 Starting Azure AI Translate Compatibility Tests...")
    
    # Check if service is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Document Processing Service is not running!")
            print("Please start the service with: python src/main.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Document Processing Service!")
        print("Please start the service with: python src/main.py")
        sys.exit(1)
    
    # Run tests
    test_azure_translate_analysis()
    test_comparison_with_legacy()
    show_azure_ai_standards()
    
    print("\n" + "=" * 60)
    print("✅ Azure AI Translate Compatibility Testing Complete!")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("   1. Review the analysis results above")
    print("   2. Address any recommendations for optimal Azure AI Translate performance")
    print("   3. Use the Azure AI analysis endpoint in your translation workflow")
    print("   4. Monitor readiness scores to ensure high-quality translations")

if __name__ == "__main__":
    main()
