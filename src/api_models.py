"""
Data models for REST API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class UploadResponse(BaseModel):
    """Response from upload endpoint"""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    upload_time: datetime = Field(..., description="Upload timestamp")
    message: str = "File uploaded successfully"

class AnalyzeRequest(BaseModel):
    """Request for analyze endpoint"""
    file_id: str = Field(..., description="File ID to analyze")
    drugs: List[str] = Field(
        default=["Codeine", "Warfarin"],
        description="List of drugs to analyze"
    )

class AnalyzeResponse(BaseModel):
    """Response from analyze endpoint"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    file_id: str = Field(..., description="Associated file ID")
    status: str = Field(default="processing", description="Analysis status")
    start_time: datetime = Field(..., description="Analysis start time")
    message: str = "Analysis queued successfully"

class ResultsResponse(BaseModel):
    """Response from results endpoint"""
    analysis_id: str = Field(..., description="Analysis ID")
    file_id: str = Field(..., description="File ID")
    status: str = Field(..., description="Analysis status (processing/completed/error)")
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    drugs_analyzed: List[str] = Field(..., description="Drugs analyzed")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Analysis results")
    error: Optional[str] = Field(None, description="Error message if failed")
    cache_stats: Optional[Dict[str, Any]] = Field(None, description="LLM cache statistics")

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="System status")
    llm_available: bool = Field(..., description="LLM services available")
    llm_provider: Optional[str] = Field(None, description="Active LLM provider")
    cache_ready: bool = Field(..., description="Cache system ready")
    version: str = Field(default="1.0.0", description="API version")
