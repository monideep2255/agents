from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from fastapi import HTTPException, status
import json

from ..models.job import Job
from ..schemas.job import JobCreate, JobUpdate, JobSearch

class JobService:
    """Service for job-related operations"""
    
    @staticmethod
    def create_job(db: Session, job_data: JobCreate) -> Job:
        """Create a new job listing"""
        # Check if job already exists
        existing_job = db.query(Job).filter(
            Job.external_id == job_data.external_id,
            Job.source == job_data.source
        ).first()
        
        if existing_job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job already exists"
            )
        
        # Create new job
        db_job = Job(
            external_id=job_data.external_id,
            source=job_data.source,
            title=job_data.title,
            company=job_data.company,
            company_url=job_data.company_url,
            location=job_data.location,
            remote_option=job_data.remote_option,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            job_type=job_data.job_type,
            experience_level=job_data.experience_level,
            description=job_data.description,
            requirements=job_data.requirements,
            benefits=job_data.benefits,
            skills_required=job_data.skills_required,
            skills_preferred=job_data.skills_preferred,
            application_url=job_data.application_url,
            posted_date=job_data.posted_date,
            application_deadline=job_data.application_deadline
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    
    @staticmethod
    def get_job(db: Session, job_id: int) -> Optional[Job]:
        """Get a job by ID"""
        return db.query(Job).filter(Job.id == job_id).first()
    
    @staticmethod
    def get_jobs(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Job]:
        """Get list of jobs with pagination"""
        query = db.query(Job)
        if active_only:
            query = query.filter(Job.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def search_jobs(db: Session, search_params: JobSearch) -> Dict[str, Any]:
        """Search jobs with various filters"""
        query = db.query(Job).filter(Job.is_active == True)
        
        # Apply filters
        if search_params.keywords:
            keywords = search_params.keywords.lower().split()
            keyword_filters = []
            for keyword in keywords:
                keyword_filters.append(
                    or_(
                        Job.title.ilike(f"%{keyword}%"),
                        Job.company.ilike(f"%{keyword}%"),
                        Job.description.ilike(f"%{keyword}%"),
                        Job.requirements.ilike(f"%{keyword}%")
                    )
                )
            query = query.filter(or_(*keyword_filters))
        
        if search_params.location:
            query = query.filter(Job.location.ilike(f"%{search_params.location}%"))
        
        if search_params.company:
            query = query.filter(Job.company.ilike(f"%{search_params.company}%"))
        
        if search_params.remote_only:
            query = query.filter(
                or_(
                    Job.remote_option == "Remote",
                    Job.remote_option == "Hybrid"
                )
            )
        
        if search_params.salary_min:
            query = query.filter(Job.salary_max >= search_params.salary_min)
        
        if search_params.salary_max:
            query = query.filter(Job.salary_min <= search_params.salary_max)
        
        if search_params.job_type:
            query = query.filter(Job.job_type == search_params.job_type)
        
        if search_params.experience_level:
            query = query.filter(Job.experience_level == search_params.experience_level)
        
        if search_params.skills:
            skill_filters = []
            for skill in search_params.skills:
                skill_filters.append(
                    or_(
                        Job.skills_required.contains([skill]),
                        Job.skills_preferred.contains([skill])
                    )
                )
            if skill_filters:
                query = query.filter(or_(*skill_filters))
        
        if search_params.sources:
            query = query.filter(Job.source.in_(search_params.sources))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        jobs = query.order_by(desc(Job.posted_date)).offset(
            search_params.offset
        ).limit(search_params.limit).all()
        
        return {
            "jobs": jobs,
            "total": total,
            "limit": search_params.limit,
            "offset": search_params.offset,
            "has_more": (search_params.offset + search_params.limit) < total
        }
    
    @staticmethod
    def update_job(db: Session, job_id: int, job_data: JobUpdate) -> Optional[Job]:
        """Update a job"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        
        # Update job fields
        update_data = job_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(job, field):
                setattr(job, field, value)
        
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def delete_job(db: Session, job_id: int) -> bool:
        """Delete a job (soft delete by setting is_active to False)"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        
        job.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_jobs_by_company(db: Session, company: str) -> List[Job]:
        """Get all jobs from a specific company"""
        return db.query(Job).filter(
            and_(
                Job.company.ilike(f"%{company}%"),
                Job.is_active == True
            )
        ).order_by(desc(Job.posted_date)).all()
    
    @staticmethod
    def get_recent_jobs(db: Session, days: int = 7) -> List[Job]:
        """Get jobs posted in the last N days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return db.query(Job).filter(
            and_(
                Job.posted_date >= cutoff_date,
                Job.is_active == True
            )
        ).order_by(desc(Job.posted_date)).all()
    
    @staticmethod
    def get_jobs_by_location(db: Session, location: str) -> List[Job]:
        """Get jobs in a specific location"""
        return db.query(Job).filter(
            and_(
                Job.location.ilike(f"%{location}%"),
                Job.is_active == True
            )
        ).order_by(desc(Job.posted_date)).all()
    
    @staticmethod
    def get_remote_jobs(db: Session) -> List[Job]:
        """Get all remote jobs"""
        return db.query(Job).filter(
            and_(
                or_(
                    Job.remote_option == "Remote",
                    Job.remote_option == "Hybrid"
                ),
                Job.is_active == True
            )
        ).order_by(desc(Job.posted_date)).all() 