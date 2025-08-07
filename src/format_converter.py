import subprocess
import os
import shutil
from pathlib import Path
from typing import Tuple, Optional
import logging
import tempfile

logger = logging.getLogger(__name__)

class FormatConverter:
    """Converts incompatible document formats to DOCX using various methods."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.libreoffice_path = self._find_libreoffice()
    
    def _find_libreoffice(self) -> Optional[str]:
        """Attempts to find LibreOffice installation path."""
        common_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "/usr/bin/libreoffice",
            "/usr/local/bin/libreoffice",
            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        ]
        
        # Check if libreoffice is in PATH
        if shutil.which("libreoffice"):
            return "libreoffice"
        if shutil.which("soffice"):
            return "soffice"
        
        # Check common installation paths
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        self.logger.warning("LibreOffice not found. Format conversion may be limited.")
        return None
    
    def convert_to_docx(self, input_file: str, output_dir: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Converts various document formats to DOCX.
        
        Args:
            input_file: Path to the input file
            output_dir: Directory to save the converted file (optional)
            
        Returns:
            Tuple of (success, message, output_file_path)
        """
        try:
            input_path = Path(input_file)
            
            if not input_path.exists():
                return False, f"Input file does not exist: {input_file}", None
            
            if not output_dir:
                output_dir = input_path.parent
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            output_filename = input_path.stem + ".docx"
            output_path = output_dir / output_filename
            
            # Check if file is already DOCX
            if input_path.suffix.lower() == '.docx':
                # Copy the file to the output location if different
                if input_path != output_path:
                    shutil.copy2(input_path, output_path)
                return True, "File is already in DOCX format", str(output_path)
            
            # Determine conversion method based on file type
            file_extension = input_path.suffix.lower()
            
            if file_extension in ['.doc', '.rtf', '.odt', '.txt']:
                return self._convert_with_libreoffice(input_path, output_dir)
            else:
                return False, f"Unsupported file format: {file_extension}", None
                
        except Exception as e:
            error_msg = f"Error converting file: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def _convert_with_libreoffice(self, input_path: Path, output_dir: Path) -> Tuple[bool, str, Optional[str]]:
        """
        Converts document using LibreOffice in headless mode.
        
        Args:
            input_path: Path to input file
            output_dir: Output directory
            
        Returns:
            Tuple of (success, message, output_file_path)
        """
        if not self.libreoffice_path:
            return False, "LibreOffice not found. Please install LibreOffice for format conversion.", None
        
        try:
            # Create temporary directory for conversion
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_output = Path(temp_dir)
                
                # LibreOffice command for conversion
                cmd = [
                    self.libreoffice_path,
                    "--headless",
                    "--convert-to", "docx",
                    "--outdir", str(temp_output),
                    str(input_path)
                ]
                
                self.logger.info(f"Running LibreOffice conversion: {' '.join(cmd)}")
                
                # Run conversion
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout
                )
                
                if result.returncode == 0:
                    # Find the converted file
                    converted_files = list(temp_output.glob("*.docx"))
                    
                    if converted_files:
                        temp_file = converted_files[0]
                        final_output = output_dir / f"{input_path.stem}.docx"
                        
                        # Move file to final location
                        shutil.move(str(temp_file), str(final_output))
                        
                        self.logger.info(f"Successfully converted {input_path} to {final_output}")
                        return True, "File converted successfully", str(final_output)
                    else:
                        return False, "Conversion completed but no output file found", None
                else:
                    error_msg = f"LibreOffice conversion failed: {result.stderr}"
                    self.logger.error(error_msg)
                    return False, error_msg, None
                    
        except subprocess.TimeoutExpired:
            return False, "Conversion timed out", None
        except Exception as e:
            error_msg = f"Error during LibreOffice conversion: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def get_supported_formats(self) -> list:
        """Returns list of supported input formats for conversion."""
        base_formats = ['.docx']  # Already supported
        
        if self.libreoffice_path:
            base_formats.extend([
                '.doc',   # Microsoft Word 97-2003
                '.rtf',   # Rich Text Format
                '.odt',   # OpenDocument Text
                '.txt',   # Plain text
            ])
        
        return base_formats
    
    def is_conversion_needed(self, file_path: str) -> bool:
        """
        Checks if a file needs conversion to DOCX format.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if conversion is needed, False if already DOCX
        """
        try:
            return Path(file_path).suffix.lower() != '.docx'
        except Exception:
            return True
