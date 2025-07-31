"""
AI Engine Main Orchestrator - Phase 2

This module orchestrates all AI agents for job analysis and matching:
- Job Analyzer Agent
- Skills Matcher Agent
- Company Research Agent
- Salary Analysis Agent
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime

# Import our agents
from agents.job_analyzer import JobAnalyzerAgent, JobAnalysisResult
from agents.skills_matcher import SkillsMatcherAgent, SkillsMatchResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobAnalysisRequest:
    """Request for job analysis"""
    job_data: Dict[str, Any]
    user_profile: Optional[Dict[str, Any]] = None
    include_skills_matching: bool = True
    include_company_research: bool = True
    include_salary_analysis: bool = True

@dataclass
class JobAnalysisResponse:
    """Complete job analysis response"""
    job_id: str
    timestamp: datetime
    job_analysis: JobAnalysisResult
    skills_matching: Optional[SkillsMatchResult] = None
    company_research: Optional[Dict[str, Any]] = None
    salary_analysis: Optional[Dict[str, Any]] = None
    overall_score: float = 0.0
    recommendations: List[str] = None

class AIEngineOrchestrator:
    """Main orchestrator for all AI agents"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the AI engine orchestrator"""
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize agents
        self.job_analyzer = JobAnalyzerAgent(self.openai_api_key)
        self.skills_matcher = SkillsMatcherAgent()
        
        logger.info("AI Engine Orchestrator initialized successfully")
    
    async def analyze_job_comprehensive(self, request: JobAnalysisRequest) -> JobAnalysisResponse:
        """
        Perform comprehensive job analysis using all available agents
        
        Args:
            request: JobAnalysisRequest with job data and user profile
            
        Returns:
            JobAnalysisResponse with complete analysis
        """
        try:
            logger.info(f"Starting comprehensive analysis for job: {request.job_data.get('title', 'Unknown')}")
            
            # Step 1: Basic job analysis
            job_analysis = await self._analyze_job(request.job_data, request.user_profile)
            
            # Step 2: Skills matching (if requested and user profile provided)
            skills_matching = None
            if request.include_skills_matching and request.user_profile:
                skills_matching = await self._match_skills(
                    request.user_profile, 
                    job_analysis.required_skills,
                    job_analysis.preferred_skills
                )
            
            # Step 3: Company research (if requested)
            company_research = None
            if request.include_company_research:
                company_research = await self._research_company(request.job_data.get('company', ''))
            
            # Step 4: Salary analysis (if requested)
            salary_analysis = None
            if request.include_salary_analysis:
                salary_analysis = await self._analyze_salary(
                    request.job_data.get('title', ''),
                    request.job_data.get('location', ''),
                    request.job_data.get('company', '')
                )
            
            # Step 5: Calculate overall score and generate recommendations
            overall_score = self._calculate_overall_score(
                job_analysis, skills_matching, company_research, salary_analysis
            )
            
            recommendations = self._generate_recommendations(
                job_analysis, skills_matching, company_research, salary_analysis
            )
            
            response = JobAnalysisResponse(
                job_id=request.job_data.get('id', ''),
                timestamp=datetime.now(),
                job_analysis=job_analysis,
                skills_matching=skills_matching,
                company_research=company_research,
                salary_analysis=salary_analysis,
                overall_score=overall_score,
                recommendations=recommendations
            )
            
            logger.info(f"Comprehensive analysis completed. Overall score: {overall_score:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            raise
    
    async def _analyze_job(self, job_data: Dict[str, Any], user_profile: Optional[Dict[str, Any]]) -> JobAnalysisResult:
        """Analyze job description using JobAnalyzerAgent"""
        try:
            return self.job_analyzer.analyze_job(job_data, user_profile)
        except Exception as e:
            logger.error(f"Error in job analysis: {str(e)}")
            raise
    
    async def _match_skills(self, user_profile: Dict[str, Any], required_skills: List[str], preferred_skills: List[str]) -> SkillsMatchResult:
        """Match user skills with job requirements"""
        try:
            user_skills = user_profile.get('skills', [])
            return self.skills_matcher.match_skills(user_skills, required_skills, preferred_skills)
        except Exception as e:
            logger.error(f"Error in skills matching: {str(e)}")
            raise
    
    async def _research_company(self, company_name: str) -> Dict[str, Any]:
        """Research company information (placeholder for future implementation)"""
        try:
            # TODO: Implement company research agent
            # For now, return basic structure
            return {
                "company_name": company_name,
                "industry": "Technology",  # Placeholder
                "size": "Medium",  # Placeholder
                "founded": "Unknown",  # Placeholder
                "location": "Unknown",  # Placeholder
                "website": "Unknown",  # Placeholder
                "description": f"Research data for {company_name} will be implemented in future phases",
                "glassdoor_rating": None,  # Placeholder
                "employee_count": None,  # Placeholder
                "revenue": None,  # Placeholder
                "culture_insights": [],  # Placeholder
                "benefits": [],  # Placeholder
                "growth_opportunities": []  # Placeholder
            }
        except Exception as e:
            logger.error(f"Error in company research: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_salary(self, job_title: str, location: str, company: str) -> Dict[str, Any]:
        """Analyze salary information (placeholder for future implementation)"""
        try:
            # TODO: Implement salary analysis agent
            # For now, return basic structure
            return {
                "job_title": job_title,
                "location": location,
                "company": company,
                "estimated_range": {
                    "min": 60000,  # Placeholder
                    "max": 120000,  # Placeholder
                    "median": 90000  # Placeholder
                },
                "market_rate": "Competitive",  # Placeholder
                "location_factor": 1.0,  # Placeholder
                "experience_multiplier": 1.0,  # Placeholder
                "benefits_value": 15000,  # Placeholder
                "total_compensation": {
                    "min": 75000,  # Placeholder
                    "max": 135000,  # Placeholder
                    "median": 105000  # Placeholder
                },
                "salary_insights": [
                    "Salary analysis will be implemented in future phases",
                    "Consider total compensation including benefits",
                    "Research market rates for your location"
                ]
            }
        except Exception as e:
            logger.error(f"Error in salary analysis: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_overall_score(self, 
                               job_analysis: JobAnalysisResult,
                               skills_matching: Optional[SkillsMatchResult],
                               company_research: Optional[Dict[str, Any]],
                               salary_analysis: Optional[Dict[str, Any]]) -> float:
        """Calculate overall job match score"""
        try:
            scores = []
            weights = []
            
            # Job quality score (30% weight)
            scores.append(job_analysis.job_quality_score / 100.0)
            weights.append(0.3)
            
            # Skills match score (40% weight)
            if skills_matching:
                scores.append(skills_matching.overall_match_score)
                weights.append(0.4)
            
            # Company research score (15% weight)
            if company_research and not company_research.get('error'):
                # Placeholder: company score based on available data
                company_score = 0.7  # Default score
                scores.append(company_score)
                weights.append(0.15)
            
            # Salary match score (15% weight)
            if salary_analysis and not salary_analysis.get('error'):
                # Placeholder: salary score based on user preferences
                salary_score = 0.8  # Default score
                scores.append(salary_score)
                weights.append(0.15)
            
            # Calculate weighted average
            if scores and weights:
                total_weight = sum(weights)
                weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
                overall_score = weighted_sum / total_weight
                return min(overall_score, 1.0)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {str(e)}")
            return 0.0
    
    def _generate_recommendations(self,
                                job_analysis: JobAnalysisResult,
                                skills_matching: Optional[SkillsMatchResult],
                                company_research: Optional[Dict[str, Any]],
                                salary_analysis: Optional[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Job quality recommendations
            if job_analysis.job_quality_score < 70:
                recommendations.append("Consider the job quality score - this position may have limited growth opportunities")
            
            # Skills gap recommendations
            if skills_matching and skills_matching.missing_skills:
                recommendations.extend(skills_matching.learning_recommendations[:3])
            
            # Company recommendations
            if company_research and not company_research.get('error'):
                recommendations.append("Research the company culture and growth opportunities before applying")
            
            # Salary recommendations
            if salary_analysis and not salary_analysis.get('error'):
                recommendations.append("Consider the total compensation package, not just base salary")
            
            # General recommendations
            recommendations.append("Customize your resume to highlight relevant skills for this position")
            recommendations.append("Prepare specific examples of your experience with the required technologies")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations"]
    
    async def batch_analyze_jobs(self, requests: List[JobAnalysisRequest]) -> List[JobAnalysisResponse]:
        """Analyze multiple jobs in batch"""
        try:
            logger.info(f"Starting batch analysis of {len(requests)} jobs")
            
            # Process jobs concurrently
            tasks = [self.analyze_job_comprehensive(request) for request in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in batch analysis: {str(result)}")
                else:
                    valid_results.append(result)
            
            logger.info(f"Batch analysis completed. Processed {len(valid_results)} out of {len(requests)} jobs")
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            raise

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
    
    # Create request
    request = JobAnalysisRequest(
        job_data=sample_job,
        user_profile=sample_profile,
        include_skills_matching=True,
        include_company_research=True,
        include_salary_analysis=True
    )
    
    # Initialize orchestrator (requires OpenAI API key)
    try:
        orchestrator = AIEngineOrchestrator()
        
        # Run analysis
        async def main():
            response = await orchestrator.analyze_job_comprehensive(request)
            print(f"Overall score: {response.overall_score:.2f}")
            print(f"Job quality: {response.job_analysis.job_quality_score}")
            print(f"Recommendations: {response.recommendations}")
        
        asyncio.run(main())
        
    except Exception as e:
        print(f"Error: {str(e)}") 