"""
Job management for REST API
Handles file storage and analysis job tracking
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import tempfile
import shutil

class JobManager:
    """Manages file uploads and analysis jobs"""
    
    def __init__(self, base_dir: str = "api_data"):
        """Initialize job manager"""
        self.base_dir = Path(base_dir)
        self.uploads_dir = self.base_dir / "uploads"
        self.jobs_dir = self.base_dir / "jobs"
        self.results_dir = self.base_dir / "results"
        
        # Create directories
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory job tracking (for single instance)
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self._load_jobs()
    
    def _load_jobs(self):
        """Load existing jobs from disk"""
        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                    self.jobs[job_data['analysis_id']] = job_data
            except Exception as e:
                print(f"Error loading job {job_file}: {e}")
    
    def create_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Create a new file upload
        
        Args:
            file_content: File bytes
            filename: Original filename
            
        Returns:
            Upload metadata with file_id
        """
        file_id = str(uuid.uuid4())
        file_path = self.uploads_dir / f"{file_id}_{filename}"
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        upload_data = {
            "file_id": file_id,
            "filename": filename,
            "file_path": str(file_path),
            "upload_time": datetime.now().isoformat(),
            "file_size": len(file_content)
        }
        
        return upload_data
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """Get file path by ID"""
        # Search for file with this ID
        for file_path in self.uploads_dir.glob(f"{file_id}_*"):
            return file_path
        return None
    
    def create_job(self, file_id: str, drugs: List[str]) -> Dict[str, Any]:
        """
        Create a new analysis job
        
        Args:
            file_id: File ID to analyze
            drugs: List of drugs to analyze
            
        Returns:
            Job metadata with analysis_id
        """
        # Verify file exists
        if not self.get_file_path(file_id):
            raise FileNotFoundError(f"File {file_id} not found")
        
        analysis_id = str(uuid.uuid4())
        job_data = {
            "analysis_id": analysis_id,
            "file_id": file_id,
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "drugs": drugs,
            "results": None,
            "error": None,
            "cache_stats": None
        }
        
        # Save job metadata
        job_file = self.jobs_dir / f"{analysis_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        # Store in memory
        self.jobs[analysis_id] = job_data
        
        return job_data
    
    def update_job(self, analysis_id: str, **kwargs):
        """Update job status and results"""
        if analysis_id not in self.jobs:
            raise ValueError(f"Job {analysis_id} not found")
        
        # Update in memory
        self.jobs[analysis_id].update(kwargs)
        
        # Save to disk
        job_file = self.jobs_dir / f"{analysis_id}.json"
        with open(job_file, 'w') as f:
            json.dump(self.jobs[analysis_id], f, indent=2)
    
    def get_job(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        return self.jobs.get(analysis_id)
    
    def mark_complete(self, analysis_id: str, results: Any, cache_stats: Dict = None):
        """Mark job as complete with results"""
        self.update_job(
            analysis_id,
            status="completed",
            end_time=datetime.now().isoformat(),
            results=results,
            cache_stats=cache_stats
        )
        
        # Save results
        results_file = self.results_dir / f"{analysis_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def mark_error(self, analysis_id: str, error: str):
        """Mark job as failed"""
        self.update_job(
            analysis_id,
            status="error",
            end_time=datetime.now().isoformat(),
            error=error
        )
    
    def cleanup_old_files(self, days: int = 7):
        """Clean up files older than specified days"""
        import time
        now = time.time()
        cutoff = now - (days * 86400)
        
        deleted_count = 0
        for file_path in self.uploads_dir.glob("*"):
            if file_path.stat().st_mtime < cutoff:
                file_path.unlink()
                deleted_count += 1
        
        return deleted_count


# Global job manager instance
_job_manager = None

def get_job_manager() -> JobManager:
    """Get or create job manager"""
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
