import zipfile
import os
from typing import Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DocumentValidator:
    """Validates document file formats and ensures they meet requirements."""
    
    VALID_DOCX_EXTENSIONS = ['.docx']
    DOCX_CONTENT_TYPES = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_file_format(self, file_path: str) -> Tuple[bool, str]:
        """
        Validates if the file is in Strict Open XML Document (*.docx) format.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            file_path = Path(file_path)
            
            # Check if file exists
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"
            
            # Check file extension
            if file_path.suffix.lower() not in self.VALID_DOCX_EXTENSIONS:
                return False, f"Invalid file extension. Expected .docx, got {file_path.suffix}"
            
            # Validate DOCX structure by checking ZIP format and content
            if not self._is_valid_docx_structure(file_path):
                return False, "File is not a valid DOCX document (invalid internal structure)"
            
            self.logger.info(f"File validation successful: {file_path}")
            return True, "File format validation passed"
            
        except Exception as e:
            error_msg = f"Error validating file format: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _is_valid_docx_structure(self, file_path: Path) -> bool:
        """
        Validates the internal structure of a DOCX file.
        DOCX files are ZIP archives with specific structure.
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Check for required DOCX components
                required_files = [
                    '[Content_Types].xml',
                    'word/document.xml'
                ]
                
                zip_contents = zip_file.namelist()
                
                for required_file in required_files:
                    if required_file not in zip_contents:
                        self.logger.warning(f"Missing required file in DOCX: {required_file}")
                        return False
                
                # Validate content types
                try:
                    content_types = zip_file.read('[Content_Types].xml').decode('utf-8')
                    if 'wordprocessingml' not in content_types:
                        self.logger.warning("DOCX content type validation failed")
                        return False
                except Exception as e:
                    self.logger.warning(f"Could not validate content types: {e}")
                    return False
                
                return True
                
        except zipfile.BadZipFile:
            self.logger.warning(f"File is not a valid ZIP archive: {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error validating DOCX structure: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Gets basic file information for validation purposes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            file_path = Path(file_path)
            stat = file_path.stat()
            
            return {
                'filename': file_path.name,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'extension': file_path.suffix.lower(),
                'exists': file_path.exists(),
                'is_file': file_path.is_file()
            }
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return {'error': str(e)}
