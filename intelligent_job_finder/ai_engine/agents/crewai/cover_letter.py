"""
Cover Letter Agent - AI-powered cover letter generation

This agent specializes in creating compelling, personalized cover letters
that showcase candidate fit and enthusiasm for specific roles and companies.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)


@dataclass
class CoverLetterRequest:
    """Request structure for cover letter generation"""
    job_title: str
    company_name: str
    job_description: str
    user_profile: Dict[str, Any]
    tailored_resume: str
    tone: str = "professional"  # 'professional', 'enthusiastic', 'confident', 'humble'
    length: str = "standard"    # 'brief', 'standard', 'detailed'
    focus_areas: Optional[List[str]] = None


@dataclass
class CoverLetterResult:
    """Result structure for cover letter generation"""
    success: bool
    cover_letter: Optional[str] = None
    tone_analysis: Optional[Dict[str, Any]] = None
    key_points: Optional[List[str]] = None
    word_count: Optional[int] = None
    error_message: Optional[str] = None


class CoverLetterAgent:
    """
    AI-powered cover letter generation agent that creates personalized cover letters.
    
    Features:
    - Company-specific customization
    - Tone and style adaptation
    - Key achievement highlighting
    - Cultural fit demonstration
    - Professional formatting
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4"):
        """
        Initialize the cover letter agent.
        
        Args:
            openai_api_key: OpenAI API key
            model_name: OpenAI model to use
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=openai_api_key,
            temperature=0.2
        )
        
        # Define tone prompts
        self.tone_prompts = {
            "professional": self._get_professional_tone(),
            "enthusiastic": self._get_enthusiastic_tone(),
            "confident": self._get_confident_tone(),
            "humble": self._get_humble_tone()
        }
        
        # Define length guidelines
        self.length_guidelines = {
            "brief": "Keep it concise, around 200-300 words",
            "standard": "Standard length, around 300-400 words",
            "detailed": "Comprehensive, around 400-500 words"
        }
        
        logger.info("CoverLetterAgent initialized successfully")
    
    def _get_professional_tone(self) -> str:
        """Get the professional tone prompt"""
        return """Use a professional, polished tone that demonstrates competence and reliability. 
        Focus on achievements and qualifications while maintaining a respectful, business-appropriate voice."""
    
    def _get_enthusiastic_tone(self) -> str:
        """Get the enthusiastic tone prompt"""
        return """Use an enthusiastic, energetic tone that shows genuine excitement for the opportunity. 
        Demonstrate passion for the role and company while maintaining professionalism."""
    
    def _get_confident_tone(self) -> str:
        """Get the confident tone prompt"""
        return """Use a confident, assertive tone that demonstrates self-assurance and capability. 
        Show conviction in your abilities while remaining respectful and professional."""
    
    def _get_humble_tone(self) -> str:
        """Get the humble tone prompt"""
        return """Use a humble, modest tone that shows willingness to learn and grow. 
        Demonstrate eagerness to contribute while acknowledging the opportunity to develop."""
    
    def analyze_company_culture(self, company_name: str, job_description: str) -> Dict[str, Any]:
        """
        Analyze company culture from job description and company information.
        
        Args:
            company_name: Name of the company
            job_description: Job description text
            
        Returns:
            Dictionary with culture analysis
        """
        try:
            prompt = f"""
            Analyze the company culture and values based on this job description and company name.
            
            Company: {company_name}
            Job Description: {job_description}
            
            Identify:
            1. Company values and culture indicators
            2. Work environment characteristics
            3. Leadership style preferences
            4. Communication style
            5. Innovation and growth focus
            
            Return a brief analysis of the company culture.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {"culture_analysis": response.content}
            
        except Exception as e:
            logger.error(f"Error analyzing company culture: {str(e)}")
            return {"culture_analysis": "Unable to analyze company culture"}
    
    def extract_key_achievements(self, user_profile: Dict[str, Any], job_requirements: str) -> List[str]:
        """
        Extract key achievements that are relevant to the job requirements.
        
        Args:
            user_profile: User's profile information
            job_requirements: Job requirements from description
            
        Returns:
            List of relevant achievements
        """
        try:
            prompt = f"""
            Extract the most relevant achievements from this user profile that match the job requirements.
            
            User Profile:
            {user_profile}
            
            Job Requirements:
            {job_requirements}
            
            Return only the most relevant achievements as a bulleted list.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            achievements = [line.strip().lstrip('- ').lstrip('* ') 
                          for line in response.content.split('\n') 
                          if line.strip() and (line.strip().startswith('-') or line.strip().startswith('*'))]
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error extracting key achievements: {str(e)}")
            return []
    
    def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetterResult:
        """
        Generate a personalized cover letter for a specific job.
        
        Args:
            request: CoverLetterRequest with all necessary information
            
        Returns:
            CoverLetterResult with generated cover letter and analysis
        """
        try:
            logger.info(f"Starting cover letter generation for {request.job_title} at {request.company_name}")
            
            # Analyze company culture
            culture_analysis = self.analyze_company_culture(request.company_name, request.job_description)
            
            # Extract key achievements
            key_achievements = self.extract_key_achievements(request.user_profile, request.job_description)
            
            # Get tone and length guidelines
            tone_guidance = self.tone_prompts.get(request.tone, self.tone_prompts["professional"])
            length_guidance = self.length_guidelines.get(request.length, self.length_guidelines["standard"])
            
            # Create the generation prompt
            generation_prompt = f"""
            You are an expert cover letter writer. Create a compelling, personalized cover letter.
            
            {tone_guidance}
            {length_guidance}
            
            Job Information:
            - Title: {request.job_title}
            - Company: {request.company_name}
            - Description: {request.job_description}
            
            Company Culture Analysis:
            {culture_analysis['culture_analysis']}
            
            Candidate Information:
            - Profile: {request.user_profile}
            - Key Achievements: {key_achievements}
            - Tailored Resume: {request.tailored_resume}
            
            Focus Areas: {request.focus_areas or ['skills', 'experience', 'cultural fit']}
            
            Create a cover letter that:
            1. Opens with a compelling introduction
            2. Demonstrates understanding of the role and company
            3. Highlights relevant achievements and skills
            4. Shows cultural fit and enthusiasm
            5. Includes a strong closing with call to action
            6. Matches the specified tone and length
            7. Is personalized to the specific company and role
            
            Format the cover letter professionally with proper paragraphs and spacing.
            """
            
            # Generate cover letter
            response = self.llm.invoke([HumanMessage(content=generation_prompt)])
            cover_letter = response.content
            
            # Analyze the generated letter
            analysis = self._analyze_cover_letter(cover_letter, request.tone)
            
            # Extract key points
            key_points = self._extract_key_points(cover_letter)
            
            # Count words
            word_count = len(cover_letter.split())
            
            result = CoverLetterResult(
                success=True,
                cover_letter=cover_letter,
                tone_analysis=analysis,
                key_points=key_points,
                word_count=word_count
            )
            
            logger.info(f"Cover letter generated successfully. Word count: {word_count}")
            return result
            
        except Exception as e:
            logger.error(f"Error in cover letter generation: {str(e)}")
            return CoverLetterResult(
                success=False,
                error_message=str(e)
            )
    
    def _analyze_cover_letter(self, cover_letter: str, target_tone: str) -> Dict[str, Any]:
        """
        Analyze the generated cover letter for tone and effectiveness.
        
        Args:
            cover_letter: The generated cover letter
            target_tone: The target tone that was requested
            
        Returns:
            Dictionary with analysis results
        """
        try:
            prompt = f"""
            Analyze this cover letter for tone, effectiveness, and professionalism.
            
            Cover Letter:
            {cover_letter}
            
            Target Tone: {target_tone}
            
            Provide analysis on:
            1. Tone consistency with target
            2. Professionalism level
            3. Persuasiveness
            4. Clarity and readability
            5. Cultural fit indicators
            
            Return a brief analysis.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {"analysis": response.content}
            
        except Exception as e:
            logger.error(f"Error analyzing cover letter: {str(e)}")
            return {"analysis": "Unable to analyze cover letter"}
    
    def _extract_key_points(self, cover_letter: str) -> List[str]:
        """
        Extract key points from the cover letter.
        
        Args:
            cover_letter: The cover letter content
            
        Returns:
            List of key points
        """
        try:
            prompt = f"""
            Extract the key points and main arguments from this cover letter.
            
            Cover Letter:
            {cover_letter}
            
            Return only the key points as a bulleted list.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            key_points = [line.strip().lstrip('- ').lstrip('* ') 
                         for line in response.content.split('\n') 
                         if line.strip() and (line.strip().startswith('-') or line.strip().startswith('*'))]
            
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []
    
    def revise_cover_letter(self, cover_letter: str, feedback: str) -> str:
        """
        Revise a cover letter based on feedback.
        
        Args:
            cover_letter: The original cover letter
            feedback: Feedback for revision
            
        Returns:
            Revised cover letter
        """
        try:
            prompt = f"""
            Revise this cover letter based on the provided feedback.
            
            Original Cover Letter:
            {cover_letter}
            
            Feedback:
            {feedback}
            
            Please revise the cover letter to address the feedback while maintaining
            its professional quality and effectiveness.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"Error revising cover letter: {str(e)}")
            return cover_letter
    
    def generate_followup_letter(self, application_id: str, company_name: str, 
                               days_since_application: int) -> str:
        """
        Generate a follow-up letter for an application.
        
        Args:
            application_id: ID of the application
            company_name: Name of the company
            days_since_application: Days since the application was submitted
            
        Returns:
            Follow-up letter content
        """
        try:
            prompt = f"""
            Create a professional follow-up letter for a job application.
            
            Company: {company_name}
            Days Since Application: {days_since_application}
            Application ID: {application_id}
            
            The follow-up letter should:
            1. Be polite and professional
            2. Reference the original application
            3. Express continued interest
            4. Ask about the status
            5. Provide additional value or updates
            6. Include contact information
            
            Keep it concise and professional.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating follow-up letter: {str(e)}")
            return "Unable to generate follow-up letter" 