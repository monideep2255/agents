"""
Resume Tailor Agent - AI-powered resume customization

This agent specializes in tailoring resumes to match specific job requirements,
optimizing for ATS systems, and highlighting relevant skills and experience.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResumeTailoringRequest:
    """Request structure for resume tailoring"""
    job_title: str
    company_name: str
    job_description: str
    user_profile: Dict[str, Any]
    resume_content: str
    target_platform: str = "general"  # 'ats', 'human', 'linkedin', 'indeed'


@dataclass
class ResumeTailoringResult:
    """Result structure for resume tailoring"""
    success: bool
    tailored_resume: Optional[str] = None
    keywords_used: Optional[List[str]] = None
    skills_highlighted: Optional[List[str]] = None
    ats_score: Optional[float] = None
    error_message: Optional[str] = None


class ResumeTailorAgent:
    """
    AI-powered resume tailoring agent that customizes resumes for specific jobs.
    
    Features:
    - Keyword optimization for ATS systems
    - Skills and experience highlighting
    - Format optimization for different platforms
    - Professional tone and style adaptation
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4"):
        """
        Initialize the resume tailor agent.
        
        Args:
            openai_api_key: OpenAI API key
            model_name: OpenAI model to use
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=openai_api_key,
            temperature=0.1
        )
        
        # Define system prompts for different platforms
        self.platform_prompts = {
            "ats": self._get_ats_prompt(),
            "human": self._get_human_prompt(),
            "linkedin": self._get_linkedin_prompt(),
            "indeed": self._get_indeed_prompt(),
            "general": self._get_general_prompt()
        }
        
        logger.info("ResumeTailorAgent initialized successfully")
    
    def _get_ats_prompt(self) -> str:
        """Get the system prompt for ATS optimization"""
        return """You are an expert resume writer specializing in ATS (Applicant Tracking System) optimization. 
        Your goal is to create resumes that pass through ATS filters and reach human recruiters.
        
        Key ATS optimization principles:
        1. Use exact keywords from the job description
        2. Include both full terms and acronyms (e.g., "Python" and "Python Programming")
        3. Use standard section headers: "Experience", "Education", "Skills", "Summary"
        4. Avoid graphics, tables, or complex formatting
        5. Use bullet points for achievements and responsibilities
        6. Include quantifiable achievements with numbers
        7. Match job title variations and industry terminology
        
        Format the resume in plain text with clear sections and bullet points."""
    
    def _get_human_prompt(self) -> str:
        """Get the system prompt for human recruiter optimization"""
        return """You are an expert resume writer who creates compelling resumes for human recruiters. 
        Your goal is to tell a compelling story that showcases the candidate's value.
        
        Human recruiter optimization principles:
        1. Create a compelling professional summary
        2. Use action verbs and achievement-focused language
        3. Tell a story of career progression and growth
        4. Highlight transferable skills and leadership experience
        5. Include relevant certifications and training
        6. Show cultural fit and soft skills
        7. Create visual hierarchy with formatting
        
        Make the resume engaging and easy to scan quickly."""
    
    def _get_linkedin_prompt(self) -> str:
        """Get the system prompt for LinkedIn optimization"""
        return """You are an expert in LinkedIn profile optimization and resume formatting for LinkedIn applications. 
        Your goal is to create resumes that work well with LinkedIn's application system.
        
        LinkedIn optimization principles:
        1. Optimize for LinkedIn's application format
        2. Include LinkedIn-specific keywords and hashtags
        3. Focus on networking and relationship-building language
        4. Highlight endorsements and recommendations
        5. Use LinkedIn's preferred formatting style
        6. Include relevant LinkedIn groups and connections
        7. Optimize for LinkedIn's search algorithm
        
        Format for LinkedIn's application system and networking focus."""
    
    def _get_indeed_prompt(self) -> str:
        """Get the system prompt for Indeed optimization"""
        return """You are an expert in Indeed resume optimization and application formatting. 
        Your goal is to create resumes that perform well on Indeed's platform.
        
        Indeed optimization principles:
        1. Use Indeed's preferred formatting and sections
        2. Include Indeed-specific keywords and job titles
        3. Optimize for Indeed's search algorithm
        4. Use Indeed's salary and location preferences
        5. Include relevant Indeed certifications
        6. Format for Indeed's application system
        7. Use Indeed's job matching features
        
        Format specifically for Indeed's platform and application system."""
    
    def _get_general_prompt(self) -> str:
        """Get the general system prompt"""
        return """You are an expert resume writer who creates professional, tailored resumes. 
        Your goal is to customize resumes to match specific job requirements and company culture.
        
        General optimization principles:
        1. Analyze job requirements and match skills
        2. Highlight relevant experience and achievements
        3. Use professional language and formatting
        4. Include quantifiable results and metrics
        5. Show career progression and growth
        6. Adapt tone to company culture
        7. Ensure clarity and readability
        
        Create a professional, tailored resume that matches the job requirements."""
    
    def extract_keywords(self, job_description: str) -> List[str]:
        """
        Extract important keywords from job description.
        
        Args:
            job_description: The job description text
            
        Returns:
            List of important keywords
        """
        try:
            prompt = f"""
            Extract the most important keywords from this job description for resume optimization.
            Focus on:
            - Technical skills and technologies
            - Soft skills and competencies
            - Industry-specific terms
            - Job title variations
            - Required qualifications
            
            Job Description:
            {job_description}
            
            Return only the keywords as a comma-separated list, no explanations.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            keywords = [kw.strip() for kw in response.content.split(',')]
            
            logger.info(f"Extracted {len(keywords)} keywords from job description")
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def analyze_skills_gap(self, user_skills: List[str], job_keywords: List[str]) -> Dict[str, Any]:
        """
        Analyze the gap between user skills and job requirements.
        
        Args:
            user_skills: List of user's skills
            job_keywords: List of job requirement keywords
            
        Returns:
            Dictionary with gap analysis results
        """
        try:
            # Convert to lowercase for comparison
            user_skills_lower = [skill.lower() for skill in user_skills]
            job_keywords_lower = [keyword.lower() for keyword in job_keywords]
            
            # Find matching skills
            matching_skills = [skill for skill in user_skills_lower 
                             if any(keyword in skill or skill in keyword 
                                   for keyword in job_keywords_lower)]
            
            # Find missing skills
            missing_skills = [keyword for keyword in job_keywords_lower 
                            if not any(skill in keyword or keyword in skill 
                                     for skill in user_skills_lower)]
            
            # Calculate match percentage
            match_percentage = len(matching_skills) / len(job_keywords_lower) * 100 if job_keywords_lower else 0
            
            return {
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "match_percentage": match_percentage,
                "total_required": len(job_keywords_lower),
                "total_matched": len(matching_skills)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skills gap: {str(e)}")
            return {"matching_skills": [], "missing_skills": [], "match_percentage": 0}
    
    def tailor_resume(self, request: ResumeTailoringRequest) -> ResumeTailoringResult:
        """
        Tailor a resume for a specific job and platform.
        
        Args:
            request: ResumeTailoringRequest with all necessary information
            
        Returns:
            ResumeTailoringResult with tailored resume and analysis
        """
        try:
            logger.info(f"Starting resume tailoring for {request.job_title} at {request.company_name}")
            
            # Extract keywords from job description
            keywords = self.extract_keywords(request.job_description)
            
            # Analyze skills gap
            user_skills = request.user_profile.get("skills", [])
            skills_analysis = self.analyze_skills_gap(user_skills, keywords)
            
            # Get appropriate system prompt
            system_prompt = self.platform_prompts.get(request.target_platform, self.platform_prompts["general"])
            
            # Create the tailoring prompt
            tailoring_prompt = f"""
            {system_prompt}
            
            Please tailor this resume for the following job:
            
            Job Title: {request.job_title}
            Company: {request.company_name}
            Job Description: {request.job_description}
            
            User Profile:
            - Skills: {', '.join(user_skills)}
            - Experience: {request.user_profile.get('experience', 'N/A')}
            - Education: {request.user_profile.get('education', 'N/A')}
            
            Important Keywords to Include: {', '.join(keywords)}
            Skills Match Analysis: {skills_analysis['match_percentage']:.1f}% match
            
            Current Resume:
            {request.resume_content}
            
            Please create a tailored resume that:
            1. Incorporates the important keywords naturally
            2. Highlights relevant skills and experience
            3. Optimizes for {request.target_platform} platform
            4. Maintains professional formatting
            5. Shows quantifiable achievements
            6. Tells a compelling story
            
            Return the complete tailored resume in the same format as the original.
            """
            
            # Generate tailored resume
            response = self.llm.invoke([HumanMessage(content=tailoring_prompt)])
            tailored_resume = response.content
            
            # Calculate ATS score (simplified)
            ats_score = self._calculate_ats_score(tailored_resume, keywords)
            
            # Extract highlighted skills
            highlighted_skills = self._extract_highlighted_skills(tailored_resume, keywords)
            
            result = ResumeTailoringResult(
                success=True,
                tailored_resume=tailored_resume,
                keywords_used=keywords,
                skills_highlighted=highlighted_skills,
                ats_score=ats_score
            )
            
            logger.info(f"Resume tailoring completed successfully. ATS Score: {ats_score:.1f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in resume tailoring: {str(e)}")
            return ResumeTailoringResult(
                success=False,
                error_message=str(e)
            )
    
    def _calculate_ats_score(self, resume_content: str, keywords: List[str]) -> float:
        """
        Calculate a simplified ATS score based on keyword presence.
        
        Args:
            resume_content: The resume content
            keywords: List of important keywords
            
        Returns:
            ATS score from 0 to 100
        """
        try:
            if not keywords:
                return 0.0
            
            resume_lower = resume_content.lower()
            keyword_matches = 0
            
            for keyword in keywords:
                if keyword.lower() in resume_lower:
                    keyword_matches += 1
            
            score = (keyword_matches / len(keywords)) * 100
            return min(score, 100.0)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Error calculating ATS score: {str(e)}")
            return 0.0
    
    def _extract_highlighted_skills(self, resume_content: str, keywords: List[str]) -> List[str]:
        """
        Extract skills that were highlighted in the tailored resume.
        
        Args:
            resume_content: The tailored resume content
            keywords: List of keywords that should be highlighted
            
        Returns:
            List of highlighted skills
        """
        try:
            resume_lower = resume_content.lower()
            highlighted = []
            
            for keyword in keywords:
                if keyword.lower() in resume_lower:
                    highlighted.append(keyword)
            
            return highlighted
            
        except Exception as e:
            logger.error(f"Error extracting highlighted skills: {str(e)}")
            return []
    
    def optimize_for_platform(self, resume_content: str, platform: str) -> str:
        """
        Optimize resume content for a specific platform.
        
        Args:
            resume_content: The resume content to optimize
            platform: Target platform ('linkedin', 'indeed', 'ats', 'human')
            
        Returns:
            Optimized resume content
        """
        try:
            platform_prompt = self.platform_prompts.get(platform, self.platform_prompts["general"])
            
            optimization_prompt = f"""
            {platform_prompt}
            
            Please optimize this resume for {platform} platform:
            
            {resume_content}
            
            Return the optimized resume with platform-specific improvements.
            """
            
            response = self.llm.invoke([HumanMessage(content=optimization_prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"Error optimizing for platform {platform}: {str(e)}")
            return resume_content 