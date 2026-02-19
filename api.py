"""
Pharmacogenomics REST API
FastAPI application with 3 main endpoints for VCF file analysis
"""
import sys
from pathlib import Path
import json
import logging
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api_models import (
    UploadResponse, AnalyzeRequest, AnalyzeResponse,
    ResultsResponse, ErrorResponse, HealthResponse
)
from src.api_job_manager import get_job_manager
from src.risk_predictor import RiskPredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PharmaGuard REST API",
    description="Pharmacogenomic Risk Assessment API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize risk predictor (cached)
_predictor = None

def get_predictor() -> RiskPredictor:
    """Get or create risk predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = RiskPredictor()
    return _predictor


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and LLM health status"""
    try:
        predictor = get_predictor()
        
        return HealthResponse(
            status="healthy",
            llm_available=predictor.llm_available,
            llm_provider=predictor.llm_explainer.provider if predictor.llm_available else None,
            cache_ready=True,
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            llm_available=False,
            cache_ready=False
        )


# ============================================================================
# ENDPOINT 1: POST /upload
# Accept VCF file and return file_id
# ============================================================================

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a VCF file
    
    - **file**: VCF file to upload
    
    Returns:
    - **file_id**: Unique identifier for uploaded file
    - **filename**: Original filename
    - **upload_time**: Timestamp of upload
    """
    try:
        # Validate file type
        if not file.filename.endswith('.vcf'):
            raise HTTPException(
                status_code=400,
                detail="Only .vcf files are accepted"
            )
        
        # Save file
        job_manager = get_job_manager()
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        upload_data = job_manager.create_upload(file_content, file.filename)
        
        logger.info(f"File uploaded: {file.filename} (ID: {upload_data['file_id']})")
        
        return UploadResponse(
            file_id=upload_data['file_id'],
            filename=upload_data['filename'],
            upload_time=upload_data['upload_time']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


# ============================================================================
# ENDPOINT 2: POST /analyze
# Accept file_id and return analysis_id
# ============================================================================

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_file(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Start analysis of an uploaded file
    
    Request body:
    - **file_id**: ID of uploaded file
    - **drugs**: List of drugs to analyze (optional, defaults to common drugs)
    
    Returns:
    - **analysis_id**: Unique identifier for this analysis
    - **status**: Current status (processing)
    - **start_time**: When analysis started
    """
    try:
        job_manager = get_job_manager()
        
        # Verify file exists
        file_path = job_manager.get_file_path(request.file_id)
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail=f"File {request.file_id} not found"
            )
        
        # Create job
        job_data = job_manager.create_job(request.file_id, request.drugs)
        
        # Queue analysis as background task
        background_tasks.add_task(
            run_analysis,
            analysis_id=job_data['analysis_id'],
            file_path=str(file_path),
            drugs=request.drugs
        )
        
        logger.info(f"Analysis queued: {job_data['analysis_id']} for file {request.file_id}")
        
        return AnalyzeResponse(
            analysis_id=job_data['analysis_id'],
            file_id=request.file_id,
            status="processing",
            start_time=job_data['start_time']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis request failed: {str(e)}"
        )


# ============================================================================
# ENDPOINT 3: GET /results/{analysis_id}
# Return analysis results
# ============================================================================

@app.get("/results/{analysis_id}", response_model=ResultsResponse)
async def get_results(analysis_id: str):
    """
    Get analysis results
    
    - **analysis_id**: ID of the analysis
    
    Returns:
    - **status**: Analysis status (processing/completed/error)
    - **results**: Analysis results (when completed)
    - **error**: Error message (if failed)
    - **cache_stats**: LLM cache statistics
    """
    try:
        job_manager = get_job_manager()
        job = job_manager.get_job(analysis_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )
        
        # Parse results if string
        results = job.get('results')
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except:
                pass
        
        return ResultsResponse(
            analysis_id=analysis_id,
            file_id=job['file_id'],
            status=job['status'],
            start_time=job['start_time'],
            end_time=job.get('end_time'),
            drugs_analyzed=job['drugs'],
            results=results,
            error=job.get('error'),
            cache_stats=job.get('cache_stats')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve results: {str(e)}"
        )


# ============================================================================
# BACKGROUND TASK: Run actual analysis
# ============================================================================

def run_analysis(analysis_id: str, file_path: str, drugs: List[str]):
    """
    Background task to run the actual VCF analysis
    Called asynchronously after analyze endpoint returns
    """
    job_manager = get_job_manager()
    
    try:
        logger.info(f"Starting analysis {analysis_id}")
        
        predictor = get_predictor()
        
        # Run prediction
        result = predictor.predict_from_vcf(file_path, drugs)
        
        if not result['success']:
            raise Exception(f"Prediction failed: {result.get('errors', 'Unknown error')}")
        
        # Parse JSON output
        json_output = json.loads(result['json_output'])
        
        # Get cache stats
        cache_stats = None
        if predictor.llm_available:
            cache_stats = predictor.llm_explainer.get_cache_stats()
        
        # Mark job as complete
        job_manager.mark_complete(
            analysis_id,
            results=json_output,
            cache_stats=cache_stats
        )
        
        logger.info(f"Analysis {analysis_id} completed successfully")
    
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {e}")
        job_manager.mark_error(analysis_id, str(e))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("PharmaGuard API starting...")
    try:
        predictor = get_predictor()
        logger.info(f"LLM Available: {predictor.llm_available}")
        if predictor.llm_available:
            logger.info(f"LLM Provider: {predictor.llm_explainer.provider}")
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("PharmaGuard API shutting down...")
    job_manager = get_job_manager()
    deleted = job_manager.cleanup_old_files(days=7)
    logger.info(f"Cleaned up {deleted} old files")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "name": "PharmaGuard REST API",
        "version": "1.0.0",
        "description": "Pharmacogenomic Risk Assessment API",
        "endpoints": {
            "health": "/health",
            "upload": "POST /upload",
            "analyze": "POST /analyze",
            "results": "GET /results/{analysis_id}",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
