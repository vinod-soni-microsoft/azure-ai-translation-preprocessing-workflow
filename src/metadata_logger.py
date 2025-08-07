import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os

class MetadataLogger:
    """Logs metadata and operations for document processing."""
    
    def __init__(self, log_directory: str = "logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = self._setup_logger()
        
        # JSON log file for structured metadata
        self.metadata_log_file = self.log_directory / "metadata.jsonl"
        
    def _setup_logger(self) -> logging.Logger:
        """Sets up the logging configuration."""
        logger = logging.getLogger("DocumentProcessor")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.log_directory / "document_processing.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_operation(self, operation: str, file_path: str, status: str, 
                     details: Dict[str, Any] = None, error: str = None):
        """
        Logs a document processing operation.
        
        Args:
            operation: Type of operation (validation, extraction, conversion, etc.)
            file_path: Path to the file being processed
            status: Operation status (success, failure, warning)
            details: Additional operation details
            error: Error message if operation failed
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Create log entry
            log_entry = {
                'timestamp': timestamp,
                'operation': operation,
                'file_path': str(file_path),
                'filename': Path(file_path).name,
                'status': status,
                'details': details or {},
                'error': error
            }
            
            # Log to structured file
            self._write_metadata_log(log_entry)
            
            # Log to text logger
            log_message = f"{operation} - {Path(file_path).name} - {status}"
            if error:
                log_message += f" - Error: {error}"
            
            if status.lower() == 'success':
                self.logger.info(log_message)
            elif status.lower() == 'failure':
                self.logger.error(log_message)
            else:
                self.logger.warning(log_message)
                
        except Exception as e:
            self.logger.error(f"Failed to log operation: {str(e)}")
    
    def log_file_metadata(self, file_path: str, metadata: Dict[str, Any]):
        """
        Logs file metadata.
        
        Args:
            file_path: Path to the file
            metadata: File metadata dictionary
        """
        try:
            file_info = self._get_file_stats(file_path)
            
            complete_metadata = {
                'timestamp': datetime.now().isoformat(),
                'operation': 'metadata_capture',
                'file_path': str(file_path),
                'filename': Path(file_path).name,
                'file_stats': file_info,
                'metadata': metadata
            }
            
            self._write_metadata_log(complete_metadata)
            self.logger.info(f"Metadata logged for {Path(file_path).name}")
            
        except Exception as e:
            self.logger.error(f"Failed to log file metadata: {str(e)}")
    
    def log_conversion_status(self, input_file: str, output_file: Optional[str], 
                            success: bool, method: str, error: str = None):
        """
        Logs document conversion operations.
        
        Args:
            input_file: Original file path
            output_file: Converted file path (if successful)
            success: Whether conversion succeeded
            method: Conversion method used
            error: Error message if conversion failed
        """
        details = {
            'conversion_method': method,
            'input_format': Path(input_file).suffix.lower(),
            'output_format': '.docx' if success else None,
            'output_file': str(output_file) if output_file else None
        }
        
        status = 'success' if success else 'failure'
        self.log_operation('conversion', input_file, status, details, error)
    
    def log_content_analysis(self, file_path: str, analysis_results: Dict[str, Any]):
        """
        Logs content analysis results.
        
        Args:
            file_path: Path to the analyzed file
            analysis_results: Results from content analysis
        """
        details = {
            'content_analysis': analysis_results,
            'has_translatable_content': analysis_results.get('has_translatable_text', False),
            'word_count': analysis_results.get('total_words', 0),
            'character_count': analysis_results.get('total_characters', 0)
        }
        
        status = 'success' if analysis_results.get('has_translatable_text') else 'warning'
        self.log_operation('content_analysis', file_path, status, details)
    
    def _write_metadata_log(self, log_entry: Dict[str, Any]):
        """Writes a log entry to the JSON Lines metadata file."""
        try:
            with open(self.metadata_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write metadata log: {str(e)}")
    
    def _get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Gets file statistics."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {'error': 'File does not exist'}
            
            stat = path.stat()
            return {
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 3),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'extension': path.suffix.lower(),
                'is_file': path.is_file()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_processing_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Gets a summary of processing operations from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Summary dictionary
        """
        try:
            if not self.metadata_log_file.exists():
                return {'error': 'No metadata log file found'}
            
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            summary = {
                'total_operations': 0,
                'successful_operations': 0,
                'failed_operations': 0,
                'operations_by_type': {},
                'files_processed': set(),
                'time_range_hours': hours
            }
            
            with open(self.metadata_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
                        
                        if entry_time >= cutoff_time:
                            summary['total_operations'] += 1
                            
                            if entry.get('status') == 'success':
                                summary['successful_operations'] += 1
                            elif entry.get('status') == 'failure':
                                summary['failed_operations'] += 1
                            
                            operation = entry.get('operation', 'unknown')
                            summary['operations_by_type'][operation] = summary['operations_by_type'].get(operation, 0) + 1
                            
                            if 'filename' in entry:
                                summary['files_processed'].add(entry['filename'])
                                
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            summary['unique_files_processed'] = len(summary['files_processed'])
            summary['files_processed'] = list(summary['files_processed'])
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}
