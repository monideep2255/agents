from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from ..config.database import get_db
from ..services.auth import AuthService
from ..services.job_service import JobService
from ..schemas.job import JobCreate, JobResponse, JobSearch, JobSearchResponse, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])
security = HTTPBearer()

@router.get("/", response_model=JobSearchResponse)
def search_jobs(
    keywords: Optional[str] = Query(None, description="Search keywords"),
    location: Optional[str] = Query(None, description="Job location"),
    company: Optional[str] = Query(None, description="Company name"),
    remote_only: Optional[bool] = Query(None, description="Remote jobs only"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, description="Maximum salary"),
    job_type: Optional[str] = Query(None, description="Job type"),
    experience_level: Optional[str] = Query(None, description="Experience level"),
    skills: Optional[str] = Query(None, description="Required skills (comma-separated)"),
    sources: Optional[str] = Query(None, description="Job sources (comma-separated)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Search jobs with various filters"""
    # Parse comma-separated strings
    skills_list = skills.split(",") if skills else None
    sources_list = sources.split(",") if sources else None
    
    search_params = JobSearch(
        keywords=keywords,
        location=location,
        company=company,
        remote_only=remote_only,
        salary_min=salary_min,
        salary_max=salary_max,
        job_type=job_type,
        experience_level=experience_level,
        skills=skills_list,
        sources=sources_list,
        limit=limit,
        offset=offset
    )
    
    try:
        result = JobService.search_jobs(db, search_params)
        return JobSearchResponse(
            jobs=[job.to_dict() for job in result["jobs"]],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = JobService.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job.to_dict()

@router.get("/recent/", response_model=List[JobResponse])
def get_recent_jobs(
    days: int = Query(7, ge=1, le=30, description="Number of days"),
    db: Session = Depends(get_db)
):
    """Get recently posted jobs"""
    try:
        jobs = JobService.get_recent_jobs(db, days)
        return [job.to_dict() for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent jobs: {str(e)}"
        )

@router.get("/company/{company}", response_model=List[JobResponse])
def get_jobs_by_company(company: str, db: Session = Depends(get_db)):
    """Get all jobs from a specific company"""
    try:
        jobs = JobService.get_jobs_by_company(db, company)
        return [job.to_dict() for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company jobs: {str(e)}"
        )

@router.get("/location/{location}", response_model=List[JobResponse])
def get_jobs_by_location(location: str, db: Session = Depends(get_db)):
    """Get jobs in a specific location"""
    try:
        jobs = JobService.get_jobs_by_location(db, location)
        return [job.to_dict() for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get location jobs: {str(e)}"
        )

@router.get("/remote/", response_model=List[JobResponse])
def get_remote_jobs(db: Session = Depends(get_db)):
    """Get all remote jobs"""
    try:
        jobs = JobService.get_remote_jobs(db)
        return [job.to_dict() for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get remote jobs: {str(e)}"
        )

# Admin routes (require authentication)
@router.post("/", response_model=JobResponse)
def create_job(
    job_data: JobCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new job (admin only)"""
    # Verify user is authenticated
    user = AuthService.get_current_user(db, credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    try:
        job = JobService.create_job(db, job_data)
        return job.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update a job (admin only)"""
    # Verify user is authenticated
    user = AuthService.get_current_user(db, credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    try:
        job = JobService.update_job(db, job_id, job_data)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return job.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete a job (admin only)"""
    # Verify user is authenticated
    user = AuthService.get_current_user(db, credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    try:
        success = JobService.delete_job(db, job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return {"message": "Job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        ) 