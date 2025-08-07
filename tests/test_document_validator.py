import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from document_validator import DocumentValidator

class TestDocumentValidator:
    
    def setup_method(self):
        """Setup for each test method."""
        self.validator = DocumentValidator()
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        is_valid, message = self.validator.validate_file_format("nonexistent.docx")
        assert not is_valid
        assert "does not exist" in message
    
    def test_validate_wrong_extension(self):
        """Test validation of file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name
        
        try:
            is_valid, message = self.validator.validate_file_format(temp_path)
            assert not is_valid
            assert "Invalid file extension" in message
        finally:
            os.unlink(temp_path)
    
    def test_get_file_info(self):
        """Test getting file information."""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name
        
        try:
            info = self.validator.get_file_info(temp_path)
            assert info['exists'] is True
            assert info['is_file'] is True
            assert info['extension'] == '.docx'
            assert info['size_bytes'] > 0
        finally:
            os.unlink(temp_path)
    
    def test_get_file_info_nonexistent(self):
        """Test getting file info for non-existent file."""
        info = self.validator.get_file_info("nonexistent.docx")
        assert info['exists'] is False
