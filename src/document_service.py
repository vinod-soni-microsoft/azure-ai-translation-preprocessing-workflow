from typing import Dict, Any, Tuple, Optional
import logging
from pathlib import Path
import tempfile
import shutil

from .document_validator import DocumentValidator
from .content_extractor import ContentExtractor
from .format_converter import FormatConverter
from .metadata_logger import MetadataLogger

class DocumentService:
    """Main orchestrator for document processing operations."""
    
    def __init__(self, log_directory: str = "logs"):
        self.validator = DocumentValidator()
        self.content_extractor = ContentExtractor()
        self.format_converter = FormatConverter()
        self.metadata_logger = MetadataLogger(log_directory)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_document(self, file_path: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Complete document processing pipeline.
        
        Args:
            file_path: Path to the input document
            output_dir: Directory for converted files (optional)
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'input_file': file_path,
            'validation': {},
            'content_analysis': {},
            'conversion': {},
            'metadata': {},
            'success': False,
            'final_docx_path': None,
            'errors': []
        }
        
        try:
            self.logger.info(f"Starting document processing for: {file_path}")
            
            # Step 1: Get file information
            file_info = self.validator.get_file_info(file_path)
            result['metadata']['file_info'] = file_info
            self.metadata_logger.log_file_metadata(file_path, file_info)
            
            # Step 2: Check if file needs conversion
            needs_conversion = self.format_converter.is_conversion_needed(file_path)
            working_file = file_path
            
            if needs_conversion:
                # Step 3: Convert file to DOCX
                conversion_success, conversion_msg, converted_path = self.format_converter.convert_to_docx(
                    file_path, output_dir
                )
                
                result['conversion'] = {
                    'needed': True,
                    'success': conversion_success,
                    'message': conversion_msg,
                    'output_path': converted_path,
                    'original_format': Path(file_path).suffix.lower()
                }
                
                self.metadata_logger.log_conversion_status(
                    file_path, converted_path, conversion_success, 'libreoffice',
                    None if conversion_success else conversion_msg
                )
                
                if not conversion_success:
                    result['errors'].append(f"Conversion failed: {conversion_msg}")
                    return result
                
                working_file = converted_path
                result['final_docx_path'] = converted_path
            else:
                result['conversion'] = {
                    'needed': False,
                    'message': 'File is already in DOCX format'
                }
                result['final_docx_path'] = file_path
            
            # Step 4: Validate DOCX format
            is_valid, validation_msg = self.validator.validate_file_format(working_file)
            result['validation'] = {
                'is_valid_docx': is_valid,
                'message': validation_msg
            }
            
            self.metadata_logger.log_operation(
                'validation', working_file, 
                'success' if is_valid else 'failure',
                result['validation'],
                None if is_valid else validation_msg
            )
            
            if not is_valid:
                result['errors'].append(f"Validation failed: {validation_msg}")
                return result
            
            # Step 5: Extract and analyze content
            has_content, content_msg, content_analysis = self.content_extractor.check_translatable_content(working_file)
            result['content_analysis'] = {
                'has_translatable_content': has_content,
                'message': content_msg,
                'analysis': content_analysis
            }
            
            self.metadata_logger.log_content_analysis(working_file, content_analysis)
            
            if not has_content:
                result['errors'].append(f"Content analysis warning: {content_msg}")
                # Don't return here - this might be a warning rather than failure
            
            # Step 6: Final success determination
            result['success'] = is_valid and (has_content or len(result['errors']) == 0)
            
            if result['success']:
                self.metadata_logger.log_operation(
                    'complete_processing', working_file, 'success',
                    {'final_docx_path': result['final_docx_path']}
                )
            else:
                self.metadata_logger.log_operation(
                    'complete_processing', working_file, 'failure',
                    {'errors': result['errors']}
                )
            
            self.logger.info(f"Document processing completed for: {file_path}")
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error during document processing: {str(e)}"
            self.logger.error(error_msg)
            result['errors'].append(error_msg)
            
            self.metadata_logger.log_operation(
                'complete_processing', file_path, 'failure',
                error=error_msg
            )
            
            return result
    
    def validate_document_only(self, file_path: str) -> Dict[str, Any]:
        """
        Validates document format without processing.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Validation results
        """
        try:
            file_info = self.validator.get_file_info(file_path)
            is_valid, message = self.validator.validate_file_format(file_path)
            
            result = {
                'file_path': file_path,
                'file_info': file_info,
                'is_valid': is_valid,
                'message': message,
                'supported_formats': self.format_converter.get_supported_formats()
            }
            
            self.metadata_logger.log_operation(
                'validation_only', file_path,
                'success' if is_valid else 'failure',
                result, None if is_valid else message
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Error during validation: {str(e)}"
            self.logger.error(error_msg)
            return {
                'file_path': file_path,
                'is_valid': False,
                'message': error_msg,
                'error': error_msg
            }
    
    def analyze_for_azure_translate(self, file_path: str) -> Dict[str, Any]:
        """
        Analyzes document for Azure AI Translate service compatibility.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Azure AI Translate compatibility analysis
        """
        try:
            self.logger.info(f"Analyzing document for Azure AI Translate: {file_path}")
            
            # First validate the document format
            file_info = self.validator.get_file_info(file_path)
            is_valid, validation_message = self.validator.validate_file_format(file_path)
            
            result = {
                'file_path': file_path,
                'file_info': file_info,
                'format_valid': is_valid,
                'validation_message': validation_message,
                'azure_analysis': {},
                'success': False
            }
            
            if not is_valid:
                result['azure_analysis'] = {
                    'azure_translate_ready': False,
                    'error': f"Invalid DOCX format: {validation_message}"
                }
                return result
            
            # Get Azure AI Translate specific analysis
            azure_summary = self.content_extractor.get_azure_translate_summary(file_path)
            
            if 'error' in azure_summary:
                result['azure_analysis'] = azure_summary
                return result
            
            result['azure_analysis'] = azure_summary
            result['success'] = True
            
            # Log the analysis
            self.metadata_logger.log_operation(
                'azure_translate_analysis', file_path,
                'success' if azure_summary.get('ready_for_translation', False) else 'analysis_complete',
                result, None
            )
            
            self.logger.info(f"Azure AI Translate analysis completed for: {file_path}")
            return result
            
        except Exception as e:
            error_msg = f"Error during Azure AI Translate analysis: {str(e)}"
            self.logger.error(error_msg)
            result = {
                'file_path': file_path,
                'format_valid': False,
                'azure_analysis': {'error': error_msg},
                'success': False
            }
            return result

    def get_processing_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Gets processing summary for the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Processing summary
        """
        return self.metadata_logger.get_processing_summary(hours)
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """
        Gets information about supported file formats.
        
        Returns:
            Dictionary with format support information
        """
        return {
            'supported_input_formats': self.format_converter.get_supported_formats(),
            'output_format': 'docx',
            'conversion_available': self.format_converter.libreoffice_path is not None,
            'libreoffice_path': self.format_converter.libreoffice_path
        }
