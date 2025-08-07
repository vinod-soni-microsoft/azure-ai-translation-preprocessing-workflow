from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Any, List
import os
import tempfile
import shutil
from pathlib import Path
import logging
from contextlib import asynccontextmanager

from document_service import DocumentService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global document service instance
document_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global document_service
    
    # Startup
    logger.info("Starting Document Processing Service")
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("converted", exist_ok=True)
    
    # Initialize document service
    document_service = DocumentService("logs")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Document Processing Service")

# Create FastAPI app
app = FastAPI(
    title="Document Processing Service",
    description="A backend service for validating, extracting content, and converting document formats",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Document Processing Service",
        "version": "1.0.0",
        "description": "Validates, extracts content, and converts document formats",
        "endpoints": {
            "POST /upload": "Upload and process a document",
            "POST /validate": "Validate document format only",
            "GET /formats": "Get supported file formats",
            "GET /summary": "Get processing summary",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Document Processing Service",
        "libreoffice_available": document_service.format_converter.libreoffice_path is not None
    }

@app.get("/formats")
async def get_supported_formats():
    """Get information about supported file formats."""
    try:
        return document_service.get_supported_formats()
    except Exception as e:
        logger.error(f"Error getting supported formats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate")
async def validate_document(file: UploadFile = File(...)):
    """
    Validate document format without full processing.
    
    Args:
        file: Uploaded file to validate
        
    Returns:
        Validation results
    """
    temp_file = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Validate the document
        result = document_service.validate_document_only(temp_file_path)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error validating document: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
    
    finally:
        # Cleanup temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")

@app.post("/upload")
async def upload_and_process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    keep_original: bool = True
):
    """
    Upload and process a document through the complete pipeline.
    
    Args:
        file: Uploaded file to process
        keep_original: Whether to keep the original file in uploads directory
        
    Returns:
        Processing results and download links
    """
    temp_file = None
    uploaded_file_path = None
    
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        converted_dir = Path("converted")
        converted_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        uploaded_file_path = upload_dir / file.filename
        with open(uploaded_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {uploaded_file_path}")
        
        # Process the document
        result = document_service.process_document(
            str(uploaded_file_path), 
            str(converted_dir)
        )
        
        # Add download information if processing was successful
        if result['success'] and result['final_docx_path']:
            final_file = Path(result['final_docx_path'])
            if final_file.exists():
                result['download_url'] = f"/download/{final_file.name}"
        
        # Schedule cleanup if not keeping original
        if not keep_original:
            background_tasks.add_task(cleanup_file, str(uploaded_file_path))
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        
        # Cleanup on error
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            background_tasks.add_task(cleanup_file, str(uploaded_file_path))
        
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/azure-translate-analysis")
async def analyze_for_azure_translate(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Analyze document for Azure AI Translate service compatibility.
    
    This endpoint provides comprehensive analysis to determine if a document
    is ready for Azure AI Translate service, including:
    - Format validation
    - Translatable content detection
    - Language analysis
    - Segmentation optimization
    - Compatibility scoring
    
    Args:
        file: DOCX file to analyze
        
    Returns:
        Azure AI Translate compatibility analysis
    """
    uploaded_file_path = None
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.docx'):
            raise HTTPException(
                status_code=400, 
                detail="Only DOCX files are supported for Azure AI Translate analysis"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            uploaded_file_path = tmp_file.name
        
        # Perform Azure AI Translate analysis
        result = document_service.analyze_for_azure_translate(uploaded_file_path)
        
        # Add file cleanup task
        background_tasks.add_task(cleanup_file, str(uploaded_file_path))
        
        return JSONResponse(content=result)
        
    except HTTPException:
        # Cleanup on HTTP error
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            background_tasks.add_task(cleanup_file, str(uploaded_file_path))
        raise
        
    except Exception as e:
        logger.error(f"Error in Azure AI Translate analysis: {e}")
        
        # Cleanup on error
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            background_tasks.add_task(cleanup_file, str(uploaded_file_path))
        
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a processed file.
    
    Args:
        filename: Name of the file to download
        
    Returns:
        File response
    """
    try:
        # Look in converted directory first, then uploads
        file_path = None
        
        converted_path = Path("converted") / filename
        upload_path = Path("uploads") / filename
        
        if converted_path.exists():
            file_path = converted_path
        elif upload_path.exists():
            file_path = upload_path
        else:
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

@app.get("/summary")
async def get_processing_summary(hours: int = 24):
    """
    Get processing summary for the last N hours.
    
    Args:
        hours: Number of hours to look back (default: 24)
        
    Returns:
        Processing summary
    """
    try:
        if hours < 1 or hours > 168:  # Limit to 1 week
            raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")
        
        summary = document_service.get_processing_summary(hours)
        return JSONResponse(content=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")

@app.delete("/cleanup")
async def cleanup_old_files(background_tasks: BackgroundTasks, days_old: int = 7):
    """
    Clean up old files from uploads and converted directories.
    
    Args:
        days_old: Delete files older than this many days
        
    Returns:
        Cleanup results
    """
    try:
        if days_old < 1:
            raise HTTPException(status_code=400, detail="days_old must be at least 1")
        
        background_tasks.add_task(cleanup_old_files_task, days_old)
        
        return {
            "message": f"Cleanup task scheduled for files older than {days_old} days",
            "status": "scheduled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")

# Background tasks
async def cleanup_file(file_path: str):
    """Background task to cleanup a single file."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not cleanup file {file_path}: {e}")

async def cleanup_old_files_task(days_old: int):
    """Background task to cleanup old files."""
    import time
    
    try:
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        cleaned_count = 0
        
        # Cleanup uploads directory
        uploads_dir = Path("uploads")
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete {file_path}: {e}")
        
        # Cleanup converted directory
        converted_dir = Path("converted")
        if converted_dir.exists():
            for file_path in converted_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete {file_path}: {e}")
        
        logger.info(f"Cleanup completed: {cleaned_count} files removed")
        
    except Exception as e:
        logger.error(f"Error during cleanup task: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
