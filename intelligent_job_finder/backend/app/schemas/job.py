from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobBase(BaseModel):
    """Base job schema"""
    title: str
    company: str
    location: Optional[str] = None
    remote_option: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None

class JobCreate(JobBase):
    """Schema for creating a job"""
    external_id: str
    source: str
    company_url: Optional[str] = None
    application_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None

class JobUpdate(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    remote_option: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    is_active: Optional[bool] = None
    ai_match_score: Optional[float] = None
    ai_analysis: Optional[Dict[str, Any]] = None

class JobResponse(JobBase):
    """Schema for job response"""
    id: int
    external_id: str
    source: str
    company_url: Optional[str] = None
    salary_currency: str = "USD"
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None
    application_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    is_active: bool
    ai_match_score: Optional[float] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobSearch(BaseModel):
    """Schema for job search parameters"""
    keywords: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    remote_only: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    limit: int = 20
    offset: int = 0

class JobSearchResponse(BaseModel):
    """Schema for job search response"""
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

class JobMatchRequest(BaseModel):
    """Schema for job matching request"""
    user_id: int
    job_id: int
    user_skills: Optional[List[str]] = None
    user_experience: Optional[str] = None
    user_salary_preference: Optional[int] = None 