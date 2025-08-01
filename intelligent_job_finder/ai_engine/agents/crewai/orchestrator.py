"""
Application Orchestrator - Main CrewAI orchestrator for job application workflow

This orchestrator coordinates all specialized agents to handle the complete
job application process from resume tailoring to application submission.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
import logging

from .resume_tailor import ResumeTailorAgent
from .cover_letter import CoverLetterAgent
from .application_agent import ApplicationAgent
from .tracking_agent import TrackingAgent
from .followup_agent import FollowupAgent

logger = logging.getLogger(__name__)


@dataclass
class ApplicationRequest:
    """Data structure for application requests"""
    user_id: str
    job_id: str
    job_title: str
    company_name: str
    job_description: str
    user_profile: Dict[str, Any]
    resume_content: str
    platform: str  # 'linkedin', 'indeed', 'glassdoor', 'company_website'
    auto_submit: bool = False


@dataclass
class ApplicationResult:
    """Data structure for application results"""
    success: bool
    tailored_resume: Optional[str] = None
    cover_letter: Optional[str] = None
    application_id: Optional[str] = None
    tracking_url: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None


class ApplicationOrchestrator:
    """
    Main orchestrator for the job application workflow.
    
    Coordinates all specialized agents to handle:
    1. Resume tailoring for specific job requirements
    2. Cover letter generation
    3. Application submission
    4. Status tracking
    5. Follow-up management
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4"):
        """
        Initialize the orchestrator with OpenAI API key.
        
        Args:
            openai_api_key: OpenAI API key for LLM access
            model_name: OpenAI model to use (default: gpt-4)
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=openai_api_key,
            temperature=0.1
        )
        
        # Initialize specialized agents
        self.resume_agent = ResumeTailorAgent(openai_api_key)
        self.cover_letter_agent = CoverLetterAgent(openai_api_key)
        self.application_agent = ApplicationAgent(openai_api_key)
        self.tracking_agent = TrackingAgent(openai_api_key)
        self.followup_agent = FollowupAgent(openai_api_key)
        
        logger.info("ApplicationOrchestrator initialized successfully")
    
    def create_application_crew(self) -> Crew:
        """
        Create the CrewAI crew with all specialized agents.
        
        Returns:
            Crew: Configured crew with all agents and tasks
        """
        # Create agents
        resume_agent = Agent(
            role="Resume Tailor Specialist",
            goal="Tailor resumes to match specific job requirements and optimize for ATS systems",
            backstory="""You are an expert resume writer with 10+ years of experience in 
            optimizing resumes for Applicant Tracking Systems (ATS) and human recruiters. 
            You understand how to highlight relevant skills and experience for specific roles.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        cover_letter_agent = Agent(
            role="Cover Letter Writer",
            goal="Create compelling, personalized cover letters that showcase candidate fit",
            backstory="""You are a professional cover letter writer who specializes in 
            creating compelling narratives that connect candidate experience with job requirements. 
            You excel at matching tone and style to company culture.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        application_agent = Agent(
            role="Application Specialist",
            goal="Handle application submission across multiple platforms with high success rate",
            backstory="""You are an expert in job application processes across various 
            platforms including LinkedIn, Indeed, Glassdoor, and company websites. 
            You understand form requirements and submission protocols.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        tracking_agent = Agent(
            role="Application Tracker",
            goal="Monitor application status and provide real-time updates",
            backstory="""You are a dedicated application tracking specialist who monitors 
            job applications across multiple platforms and provides timely status updates 
            to candidates.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Create tasks
        resume_task = Task(
            description="""Analyze the job description and user profile to create a 
            tailored resume that highlights relevant skills and experience. 
            Optimize for ATS systems and ensure it matches the job requirements.
            
            Job Title: {job_title}
            Company: {company_name}
            Job Description: {job_description}
            User Profile: {user_profile}
            Current Resume: {resume_content}
            
            Return a tailored resume that:
            1. Highlights relevant skills and experience
            2. Uses keywords from the job description
            3. Is optimized for ATS systems
            4. Maintains professional formatting
            """,
            agent=resume_agent,
            expected_output="Tailored resume content optimized for the specific job"
        )
        
        cover_letter_task = Task(
            description="""Create a compelling cover letter for the specific job and company.
            Use the tailored resume and job information to craft a personalized letter.
            
            Job Title: {job_title}
            Company: {company_name}
            Job Description: {job_description}
            Tailored Resume: {tailored_resume}
            
            The cover letter should:
            1. Be personalized to the company and role
            2. Highlight relevant experience and skills
            3. Show enthusiasm for the opportunity
            4. Be concise and professional
            5. Include a clear call to action
            """,
            agent=cover_letter_agent,
            expected_output="Professional cover letter tailored to the job and company"
        )
        
        application_task = Task(
            description="""Submit the application using the tailored resume and cover letter.
            Handle the application process for the specified platform.
            
            Platform: {platform}
            Job Title: {job_title}
            Company: {company_name}
            Tailored Resume: {tailored_resume}
            Cover Letter: {cover_letter}
            Auto Submit: {auto_submit}
            
            If auto_submit is True, proceed with submission.
            If False, prepare the application for manual review.
            """,
            agent=application_agent,
            expected_output="Application submission result with tracking information"
        )
        
        tracking_task = Task(
            description="""Set up tracking for the submitted application and monitor its status.
            
            Application ID: {application_id}
            Platform: {platform}
            Company: {company_name}
            Job Title: {job_title}
            
            Establish tracking mechanisms and provide initial status.
            """,
            agent=tracking_agent,
            expected_output="Tracking setup confirmation and initial status"
        )
        
        # Create crew
        crew = Crew(
            agents=[resume_agent, cover_letter_agent, application_agent, tracking_agent],
            tasks=[resume_task, cover_letter_task, application_task, tracking_task],
            verbose=True,
            memory=True
        )
        
        return crew
    
    def process_application(self, request: ApplicationRequest) -> ApplicationResult:
        """
        Process a complete job application workflow.
        
        Args:
            request: ApplicationRequest containing all necessary information
            
        Returns:
            ApplicationResult: Result of the application process
        """
        try:
            logger.info(f"Starting application process for job: {request.job_title} at {request.company_name}")
            
            # Create crew
            crew = self.create_application_crew()
            
            # Prepare context for tasks
            context = {
                "job_title": request.job_title,
                "company_name": request.company_name,
                "job_description": request.job_description,
                "user_profile": request.user_profile,
                "resume_content": request.resume_content,
                "platform": request.platform,
                "auto_submit": request.auto_submit
            }
            
            # Execute the crew workflow
            result = crew.kickoff(inputs=context)
            
            # Parse results and create response
            application_result = ApplicationResult(
                success=True,
                tailored_resume=result.get("tailored_resume"),
                cover_letter=result.get("cover_letter"),
                application_id=result.get("application_id"),
                tracking_url=result.get("tracking_url"),
                status="submitted"
            )
            
            logger.info(f"Application process completed successfully for {request.job_title}")
            return application_result
            
        except Exception as e:
            logger.error(f"Error in application process: {str(e)}")
            return ApplicationResult(
                success=False,
                error_message=str(e),
                status="failed"
            )
    
    def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """
        Get the current status of an application.
        
        Args:
            application_id: ID of the application to track
            
        Returns:
            Dict containing status information
        """
        try:
            return self.tracking_agent.get_status(application_id)
        except Exception as e:
            logger.error(f"Error getting application status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def schedule_followup(self, application_id: str, followup_type: str = "standard") -> bool:
        """
        Schedule a follow-up for an application.
        
        Args:
            application_id: ID of the application
            followup_type: Type of follow-up ('standard', 'aggressive', 'polite')
            
        Returns:
            bool: True if follow-up was scheduled successfully
        """
        try:
            return self.followup_agent.schedule_followup(application_id, followup_type)
        except Exception as e:
            logger.error(f"Error scheduling follow-up: {str(e)}")
            return False 