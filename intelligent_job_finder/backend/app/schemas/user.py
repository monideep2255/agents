from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_salary_min: Optional[int] = None
    preferred_salary_max: Optional[int] = None
    remote_preference: Optional[str] = None
    skills: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        return v

class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_salary_min: Optional[int] = None
    preferred_salary_max: Optional[int] = None
    remote_preference: Optional[str] = None
    skills: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_verified: bool
    resume_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    user_id: Optional[int] = None 