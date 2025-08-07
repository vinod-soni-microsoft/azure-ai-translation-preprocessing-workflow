<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Document Processing Service Instructions

This is a Python backend service for document validation and processing. The service handles:

1. **Document Format Validation**: Validates that files are in Strict Open XML Document (*.docx) format
2. **Content Extraction**: Extracts and verifies presence of translatable text
3. **Format Conversion**: Converts incompatible formats using python-docx and LibreOffice
4. **Metadata Logging**: Logs file operations, metadata, and conversion status

## Key Components:
- `src/document_validator.py`: Handles file format validation
- `src/content_extractor.py`: Extracts and analyzes document content
- `src/format_converter.py`: Converts incompatible document formats
- `src/metadata_logger.py`: Logs operations and metadata
- `src/main.py`: FastAPI application entry point
- `src/document_service.py`: Main service orchestrator

## Dependencies:
- FastAPI for REST API
- python-docx for DOCX manipulation
- python-libreoffice for format conversion
- zipfile for format validation
- logging for operation tracking

When generating code:
- Follow Python best practices and PEP 8
- Use type hints throughout
- Implement proper error handling
- Log all operations for auditing
- Validate inputs rigorously
- Use async/await for I/O operations where appropriate
