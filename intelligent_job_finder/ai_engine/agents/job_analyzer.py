"""
Job Analyzer Agent - Phase 2 AI Component

This agent analyzes job descriptions to extract:
- Required skills and qualifications
- Company information
- Salary insights
- Job quality metrics
- Match scoring
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobAnalysisResult:
    """Result of job analysis"""
    job_id: str
    title: str
    company: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    salary_range: Optional[Dict[str, int]]
    job_quality_score: float
    company_insights: Dict[str, Any]
    match_score: float
    analysis_summary: str

class JobAnalysis(BaseModel):
    """Pydantic model for structured job analysis output"""
    required_skills: List[str] = Field(description="List of required technical and soft skills")
    preferred_skills: List[str] = Field(description="List of preferred but not required skills")
    experience_level: str = Field(description="Experience level: Entry, Mid, Senior, Lead, Executive")
    salary_range: Optional[Dict[str, int]] = Field(description="Estimated salary range with min and max")
    job_quality_score: float = Field(description="Job quality score from 0-100")
    company_insights: Dict[str, Any] = Field(description="Company information and insights")
    match_score: float = Field(description="Match score from 0-100 based on user profile")
    analysis_summary: str = Field(description="Brief summary of the job analysis")

class JobAnalyzerAgent:
    """AI agent for analyzing job descriptions"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the job analyzer agent"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI model
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=self.openai_api_key
        )
        
        # Initialize output parser
        self.output_parser = PydanticOutputParser(pydantic_object=JobAnalysis)
        
        # Create analysis prompt
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", self._get_human_prompt())
        ])
        
        logger.info("JobAnalyzerAgent initialized successfully")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for job analysis"""
        return """You are an expert job analyst with deep knowledge of:
1. Technical skills and qualifications across various industries
2. Salary ranges and market rates
3. Company analysis and insights
4. Job quality assessment

Your task is to analyze job descriptions and extract structured information.
Be precise, objective, and provide actionable insights.

Output Format:
{format_instructions}

Guidelines:
- Extract both required and preferred skills
- Provide realistic salary estimates based on location and experience
- Assess job quality based on benefits, growth opportunities, and company reputation
- Calculate match scores based on provided user profile
- Provide company insights including size, industry, and culture indicators
"""

    def _get_human_prompt(self) -> str:
        """Get the human prompt template"""
        return """Analyze the following job description:

Job Title: {job_title}
Company: {company}
Location: {location}
Job Description: {job_description}

User Profile (for match scoring):
{user_profile}

Please provide a comprehensive analysis following the specified format."""

    def analyze_job(self, 
                   job_data: Dict[str, Any], 
                   user_profile: Optional[Dict[str, Any]] = None) -> JobAnalysisResult:
        """
        Analyze a job description and return structured results
        
        Args:
            job_data: Dictionary containing job information
            user_profile: Optional user profile for match scoring
            
        Returns:
            JobAnalysisResult with comprehensive analysis
        """
        try:
            logger.info(f"Analyzing job: {job_data.get('title', 'Unknown')}")
            
            # Prepare user profile for analysis
            profile_text = self._format_user_profile(user_profile) if user_profile else "No user profile provided"
            
            # Create the analysis prompt
            messages = self.analysis_prompt.format_messages(
                format_instructions=self.output_parser.get_format_instructions(),
                job_title=job_data.get('title', ''),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                job_description=job_data.get('description', ''),
                user_profile=profile_text
            )
            
            # Get analysis from LLM
            response = self.llm.invoke(messages)
            
            # Parse the response
            analysis = self.output_parser.parse(response.content)
            
            # Create result object
            result = JobAnalysisResult(
                job_id=job_data.get('id', ''),
                title=job_data.get('title', ''),
                company=job_data.get('company', ''),
                required_skills=analysis.required_skills,
                preferred_skills=analysis.preferred_skills,
                experience_level=analysis.experience_level,
                salary_range=analysis.salary_range,
                job_quality_score=analysis.job_quality_score,
                company_insights=analysis.company_insights,
                match_score=analysis.match_score,
                analysis_summary=analysis.analysis_summary
            )
            
            logger.info(f"Job analysis completed successfully. Quality score: {result.job_quality_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing job: {str(e)}")
            raise
    
    def _format_user_profile(self, user_profile: Dict[str, Any]) -> str:
        """Format user profile for analysis"""
        if not user_profile:
            return "No user profile provided"
        
        profile_parts = []
        
        if user_profile.get('skills'):
            profile_parts.append(f"Skills: {', '.join(user_profile['skills'])}")
        
        if user_profile.get('experience_years'):
            profile_parts.append(f"Experience: {user_profile['experience_years']} years")
        
        if user_profile.get('education'):
            profile_parts.append(f"Education: {user_profile['education']}")
        
        if user_profile.get('preferred_salary'):
            profile_parts.append(f"Preferred Salary: ${user_profile['preferred_salary']}")
        
        if user_profile.get('location'):
            profile_parts.append(f"Location: {user_profile['location']}")
        
        return "\n".join(profile_parts) if profile_parts else "Basic user profile"
    
    def batch_analyze_jobs(self, 
                          jobs_data: List[Dict[str, Any]], 
                          user_profile: Optional[Dict[str, Any]] = None) -> List[JobAnalysisResult]:
        """
        Analyze multiple jobs in batch
        
        Args:
            jobs_data: List of job dictionaries
            user_profile: Optional user profile for match scoring
            
        Returns:
            List of JobAnalysisResult objects
        """
        results = []
        
        for job_data in jobs_data:
            try:
                result = self.analyze_job(job_data, user_profile)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing job {job_data.get('id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Batch analysis completed. Processed {len(results)} out of {len(jobs_data)} jobs")
        return results

# Example usage
if __name__ == "__main__":
    # Example job data
    sample_job = {
        "id": "job_001",
        "title": "Senior Python Developer",
        "company": "TechCorp Inc",
        "location": "San Francisco, CA",
        "description": """
        We are looking for a Senior Python Developer to join our growing team.
        
        Requirements:
        - 5+ years of Python development experience
        - Experience with Django, Flask, or FastAPI
        - Knowledge of databases (PostgreSQL, MySQL)
        - Experience with cloud platforms (AWS, GCP)
        - Strong problem-solving skills
        
        Preferred:
        - Experience with machine learning libraries
        - Knowledge of Docker and Kubernetes
        - Experience with microservices architecture
        
        We offer competitive salary, health benefits, and remote work options.
        """
    }
    
    # Example user profile
    sample_profile = {
        "skills": ["Python", "Django", "PostgreSQL", "AWS"],
        "experience_years": 4,
        "education": "Bachelor's in Computer Science",
        "preferred_salary": 120000,
        "location": "San Francisco, CA"
    }
    
    # Initialize analyzer (requires OpenAI API key)
    try:
        analyzer = JobAnalyzerAgent()
        result = analyzer.analyze_job(sample_job, sample_profile)
        print(f"Analysis completed: {result.analysis_summary}")
        print(f"Match score: {result.match_score}")
        print(f"Required skills: {result.required_skills}")
    except Exception as e:
        print(f"Error: {str(e)}") 