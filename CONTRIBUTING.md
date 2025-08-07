# Contributing to Document Processing Service

Thank you for your interest in contributing to the Document Processing Service! We welcome contributions from the community and are pleased to have you join us.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Operating system and version
   - Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Sample files (if applicable)

### Suggesting Enhancements

1. **Check the roadmap** in the issues section
2. **Open a discussion** for major changes
3. **Provide clear use cases** and benefits
4. **Consider Azure AI Translate compatibility** in proposals

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/document-processing-service.git
   cd document-processing-service
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

#### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following our coding standards
3. **Run tests** to ensure everything works:
   ```bash
   python test_service.py
   python test_api.py
   python test_azure_translate.py
   ```
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Commit your changes**:
   ```bash
   git commit -m "feat: add new Azure AI analysis feature"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a pull request**

## 📝 Coding Standards

### Python Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** for all function parameters and return values
- Write **descriptive docstrings** for all classes and functions
- Keep functions **focused and small** (max 50 lines)
- Use **meaningful variable names**

#### Example:

```python
from typing import Dict, List, Optional
import logging

def analyze_document_content(
    file_path: str, 
    include_metadata: bool = True
) -> Dict[str, any]:
    """
    Analyze document content for Azure AI Translate compatibility.
    
    Args:
        file_path: Path to the document file
        include_metadata: Whether to include file metadata in analysis
        
    Returns:
        Dictionary containing analysis results and recommendations
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValidationError: If the file format is invalid
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting analysis for: {file_path}")
    
    # Implementation here...
    
    return analysis_result
```

### FastAPI Standards

- Use **Pydantic models** for request/response validation
- Include **comprehensive documentation** in endpoint docstrings
- Implement **proper error handling** with appropriate HTTP status codes
- Use **dependency injection** for shared functionality

#### Example:

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List

class DocumentAnalysisRequest(BaseModel):
    include_azure_analysis: bool = True
    include_language_detection: bool = True

class DocumentAnalysisResponse(BaseModel):
    success: bool
    azure_compatible: bool
    readiness_score: str
    recommendations: List[str]

@app.post(
    "/analyze-document",
    response_model=DocumentAnalysisResponse,
    summary="Analyze document for Azure AI Translate compatibility",
    description="Comprehensive document analysis including format validation, "
                "content extraction, and Azure AI Translate readiness assessment."
)
async def analyze_document(
    file: UploadFile = File(...),
    request: DocumentAnalysisRequest = Depends(),
    service: DocumentService = Depends(get_document_service)
) -> DocumentAnalysisResponse:
    """
    Analyze uploaded document for Azure AI Translate service compatibility.
    
    This endpoint provides comprehensive analysis including:
    - DOCX format validation
    - Content extraction and segmentation
    - Language detection
    - Translation readiness scoring
    - Actionable recommendations
    """
    try:
        result = await service.analyze_for_azure_translate(file, request)
        return DocumentAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Testing Standards

- **Write tests** for all new functionality
- Achieve **minimum 80% code coverage**
- Include both **unit tests** and **integration tests**
- Test **error conditions** and edge cases
- Use **descriptive test names**

#### Example:

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAzureTranslateAnalysis:
    """Test suite for Azure AI Translate analysis functionality."""
    
    def test_valid_docx_analysis_returns_success(self):
        """Test that valid DOCX file returns successful analysis."""
        with open("tests/fixtures/valid_document.docx", "rb") as f:
            response = client.post(
                "/azure-translate-analysis",
                files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "azure_analysis" in data
        assert data["azure_analysis"]["azure_compatibility"] is True
    
    def test_invalid_file_format_returns_error(self):
        """Test that invalid file format returns appropriate error."""
        with open("tests/fixtures/fake_docx.txt", "rb") as f:
            response = client.post(
                "/azure-translate-analysis",
                files={"file": ("fake.docx", f, "text/plain")}
            )
        
        assert response.status_code == 400
        data = response.json()
        assert "invalid format" in data["detail"].lower()
```

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suite
python test_azure_translate.py

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run performance tests
python -m pytest tests/performance/ -v
```

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes
   - Mock external dependencies
   - Fast execution (< 1 second per test)

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real dependencies where appropriate
   - Moderate execution time (< 10 seconds per test)

3. **API Tests** (`tests/api/`)
   - Test REST API endpoints
   - Use TestClient for FastAPI testing
   - Include authentication and authorization tests

4. **Azure Compatibility Tests** (`tests/azure/`)
   - Test Azure AI Translate specific functionality
   - Validate compliance with Azure standards
   - Test readiness scoring accuracy

## 📚 Documentation Guidelines

### Code Documentation

- **Docstrings**: Use Google-style docstrings
- **Type hints**: Required for all public functions
- **Comments**: Explain complex logic, not obvious code
- **README updates**: Update README.md for user-facing changes

### API Documentation

- **OpenAPI/Swagger**: Automatically generated from FastAPI
- **Examples**: Include request/response examples
- **Error codes**: Document all possible error responses
- **Rate limits**: Document any limitations

## 🚀 Azure AI Translate Compliance

When contributing features related to Azure AI Translate:

### Standards to Follow

1. **Format Validation**
   - Ensure Strict Open XML Document compliance
   - Validate against Azure service requirements
   - Test with various DOCX versions

2. **Content Analysis**
   - Implement intelligent text filtering
   - Respect 5,000 character segment limits
   - Include language detection capabilities

3. **Readiness Scoring**
   - Provide quantified compatibility assessment (0-100%)
   - Include actionable recommendations
   - Validate against known Azure AI standards

4. **Performance Optimization**
   - Optimize for Azure API usage patterns
   - Minimize unnecessary API calls
   - Implement efficient content segmentation

## 🔄 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version** in `__init__.py` and `pyproject.toml`
2. **Update CHANGELOG.md** with new features and fixes
3. **Run comprehensive tests**:
   ```bash
   python test_service.py
   python test_api.py
   python test_azure_translate.py
   python test_integration.py
   ```
4. **Update documentation** as needed
5. **Create release branch**: `release/v1.2.3`
6. **Tag the release**: `git tag v1.2.3`
7. **Create GitHub release** with release notes

## 🏷️ Commit Message Guidelines

Use conventional commits format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples:
```bash
feat(azure): add readiness scoring for Azure AI Translate analysis
fix(validator): resolve DOCX format detection for Office 365 files
docs(api): update endpoint documentation with new examples
test(azure): add comprehensive Azure AI compatibility tests
```

## 🤔 Questions?

- **General questions**: Open a [Discussion](https://github.com/yourusername/document-processing-service/discussions)
- **Bug reports**: Create an [Issue](https://github.com/yourusername/document-processing-service/issues)
- **Feature requests**: Start with a [Discussion](https://github.com/yourusername/document-processing-service/discussions)
- **Security issues**: Email security@yourproject.com

## 🎉 Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** section

Thank you for contributing to the Document Processing Service! 🚀
