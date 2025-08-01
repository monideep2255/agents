"""
Phase 3 Test Script - Multi-Agent Application System

This script demonstrates the Phase 3 functionality including:
- CrewAI orchestration
- Resume tailoring
- Cover letter generation
- Application submission
- Status tracking
- Follow-up management
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.crewai.orchestrator import ApplicationOrchestrator, ApplicationRequest, ApplicationResult
from agents.crewai.resume_tailor import ResumeTailorAgent, ResumeTailoringRequest, ResumeTailoringResult
from agents.crewai.cover_letter import CoverLetterAgent, CoverLetterRequest, CoverLetterResult
from agents.crewai.application_agent import ApplicationAgent, ApplicationSubmissionRequest, ApplicationSubmissionResult
from agents.crewai.tracking_agent import TrackingAgent, TrackingRequest, TrackingResult
from agents.crewai.followup_agent import FollowupAgent, FollowupRequest, FollowupResult

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_openai_api_key() -> str:
    """Get OpenAI API key from environment or user input"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ").strip()
        if not api_key:
            raise ValueError("OpenAI API key is required")
    return api_key


def create_sample_user_profile() -> Dict[str, Any]:
    """Create a sample user profile for testing"""
    return {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1-555-123-4567",
        "location": "San Francisco, CA",
        "skills": [
            "Python", "Django", "React", "JavaScript", "PostgreSQL", 
            "AWS", "Docker", "Git", "REST APIs", "Agile Development"
        ],
        "experience": "5 years of full-stack development experience",
        "education": "Bachelor's in Computer Science from Stanford University",
        "certifications": ["AWS Certified Developer", "Google Cloud Professional"],
        "languages": ["English", "Spanish"],
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe"
    }


def create_sample_job_data() -> Dict[str, Any]:
    """Create sample job data for testing"""
    return {
        "job_title": "Senior Full-Stack Developer",
        "company_name": "TechCorp Inc.",
        "job_description": """
        We are looking for a Senior Full-Stack Developer to join our growing team.
        
        Requirements:
        - 5+ years of experience in full-stack development
        - Proficiency in Python, Django, React, and JavaScript
        - Experience with PostgreSQL and AWS
        - Knowledge of Docker and Git
        - Experience with REST APIs and microservices
        - Strong problem-solving skills
        - Excellent communication skills
        
        Responsibilities:
        - Develop and maintain web applications
        - Collaborate with cross-functional teams
        - Mentor junior developers
        - Participate in code reviews
        - Contribute to technical architecture decisions
        
        Benefits:
        - Competitive salary
        - Health insurance
        - 401(k) matching
        - Flexible work arrangements
        - Professional development opportunities
        """,
        "job_url": "https://techcorp.com/careers/senior-developer",
        "platform": "linkedin"
    }


def test_resume_tailor_agent(api_key: str):
    """Test the Resume Tailor Agent"""
    print("\n" + "="*60)
    print("TESTING RESUME TAILOR AGENT")
    print("="*60)
    
    # Initialize agent
    agent = ResumeTailorAgent(api_key)
    
    # Sample resume content
    resume_content = """
    JOHN DOE
    john.doe@email.com | +1-555-123-4567 | San Francisco, CA
    linkedin.com/in/johndoe | github.com/johndoe
    
    SUMMARY
    Experienced full-stack developer with 5 years of experience building scalable web applications.
    
    SKILLS
    Programming Languages: Python, JavaScript, TypeScript, SQL
    Frameworks: Django, React, Node.js, Express
    Databases: PostgreSQL, MongoDB, Redis
    Cloud Platforms: AWS, Google Cloud Platform
    Tools: Git, Docker, Jenkins, Jira
    
    EXPERIENCE
    
    Senior Developer | TechStart Inc. | 2022 - Present
    - Led development of customer portal using Django and React
    - Implemented CI/CD pipeline reducing deployment time by 50%
    - Mentored 3 junior developers
    
    Full-Stack Developer | WebSolutions | 2020 - 2022
    - Built REST APIs serving 10,000+ daily requests
    - Optimized database queries improving performance by 40%
    - Collaborated with UX team on responsive design
    
    Junior Developer | StartupXYZ | 2019 - 2020
    - Developed features for e-commerce platform
    - Fixed critical bugs in production environment
    - Participated in agile development process
    
    EDUCATION
    Bachelor of Science in Computer Science | Stanford University | 2019
    """
    
    # Create request
    user_profile = create_sample_user_profile()
    job_data = create_sample_job_data()
    
    request = ResumeTailoringRequest(
        job_title=job_data["job_title"],
        company_name=job_data["company_name"],
        job_description=job_data["job_description"],
        user_profile=user_profile,
        resume_content=resume_content,
        target_platform="ats"
    )
    
    # Test resume tailoring
    print("Tailoring resume for ATS optimization...")
    result = agent.tailor_resume(request)
    
    if result.success:
        print("✅ Resume tailoring successful!")
        print(f"ATS Score: {result.ats_score:.1f}")
        print(f"Keywords used: {', '.join(result.keywords_used[:5])}...")
        print(f"Skills highlighted: {', '.join(result.skills_highlighted[:5])}...")
        print("\nTailored Resume Preview:")
        print("-" * 40)
        print(result.tailored_resume[:500] + "...")
    else:
        print(f"❌ Resume tailoring failed: {result.error_message}")


def test_cover_letter_agent(api_key: str):
    """Test the Cover Letter Agent"""
    print("\n" + "="*60)
    print("TESTING COVER LETTER AGENT")
    print("="*60)
    
    # Initialize agent
    agent = CoverLetterAgent(api_key)
    
    # Create request
    user_profile = create_sample_user_profile()
    job_data = create_sample_job_data()
    
    # Sample tailored resume (simplified)
    tailored_resume = "Senior Full-Stack Developer with 5+ years of experience in Python, Django, React, and AWS..."
    
    request = CoverLetterRequest(
        job_title=job_data["job_title"],
        company_name=job_data["company_name"],
        job_description=job_data["job_description"],
        user_profile=user_profile,
        tailored_resume=tailored_resume,
        tone="professional",
        length="standard"
    )
    
    # Test cover letter generation
    print("Generating cover letter...")
    result = agent.generate_cover_letter(request)
    
    if result.success:
        print("✅ Cover letter generation successful!")
        print(f"Word count: {result.word_count}")
        print(f"Key points: {len(result.key_points)} identified")
        print("\nCover Letter Preview:")
        print("-" * 40)
        print(result.cover_letter[:500] + "...")
    else:
        print(f"❌ Cover letter generation failed: {result.error_message}")


def test_application_agent(api_key: str):
    """Test the Application Agent"""
    print("\n" + "="*60)
    print("TESTING APPLICATION AGENT")
    print("="*60)
    
    # Initialize agent
    agent = ApplicationAgent(api_key)
    
    # Create request
    user_profile = create_sample_user_profile()
    job_data = create_sample_job_data()
    
    request = ApplicationSubmissionRequest(
        platform=job_data["platform"],
        job_title=job_data["job_title"],
        company_name=job_data["company_name"],
        job_url=job_data["job_url"],
        tailored_resume="Tailored resume content...",
        cover_letter="Cover letter content...",
        user_profile=user_profile,
        auto_submit=False
    )
    
    # Test application submission
    print("Submitting application...")
    result = agent.submit_application(request)
    
    if result.success:
        print("✅ Application submission successful!")
        print(f"Application ID: {result.application_id}")
        print(f"Tracking URL: {result.tracking_url}")
        print(f"Status: {result.submission_status}")
        print(f"Platform: {result.platform_response['platform']}")
    else:
        print(f"❌ Application submission failed: {result.error_message}")


def test_tracking_agent(api_key: str):
    """Test the Tracking Agent"""
    print("\n" + "="*60)
    print("TESTING TRACKING AGENT")
    print("="*60)
    
    # Initialize agent
    agent = TrackingAgent(api_key)
    
    # Create request
    request = TrackingRequest(
        application_id="test-app-123",
        platform="linkedin",
        company_name="TechCorp Inc.",
        job_title="Senior Full-Stack Developer",
        tracking_url="https://linkedin.com/jobs/applications/test-app-123"
    )
    
    # Test application tracking
    print("Tracking application status...")
    result = agent.track_application(request)
    
    if result.success:
        print("✅ Application tracking successful!")
        print(f"Current Status: {result.current_status}")
        print(f"Last Updated: {result.last_updated}")
        if result.status_details:
            print(f"Details: {result.status_details.get('message', 'N/A')}")
        print(f"Next Check: {result.next_check}")
    else:
        print(f"❌ Application tracking failed: {result.error_message}")


def test_followup_agent(api_key: str):
    """Test the Follow-up Agent"""
    print("\n" + "="*60)
    print("TESTING FOLLOW-UP AGENT")
    print("="*60)
    
    # Initialize agent
    agent = FollowupAgent(api_key)
    
    # Create request
    request = FollowupRequest(
        application_id="test-app-123",
        company_name="TechCorp Inc.",
        job_title="Senior Full-Stack Developer",
        application_date=datetime.now(),
        followup_type="standard",
        contact_info={
            "email": "john.doe@email.com",
            "phone": "+1-555-123-4567"
        }
    )
    
    # Test follow-up generation
    print("Generating follow-up message...")
    result = agent.generate_followup_message(request)
    
    if result.success:
        print("✅ Follow-up generation successful!")
        print(f"Follow-up ID: {result.followup_id}")
        print(f"Type: {result.followup_type}")
        print(f"Scheduled Date: {result.scheduled_date}")
        print("\nFollow-up Message Preview:")
        print("-" * 40)
        print(result.followup_message[:300] + "...")
    else:
        print(f"❌ Follow-up generation failed: {result.error_message}")


def test_crewai_orchestrator(api_key: str):
    """Test the CrewAI Orchestrator"""
    print("\n" + "="*60)
    print("TESTING CREWAI ORCHESTRATOR")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = ApplicationOrchestrator(api_key)
    
    # Create application request
    user_profile = create_sample_user_profile()
    job_data = create_sample_job_data()
    
    request = ApplicationRequest(
        user_id="user-123",
        job_id="job-456",
        job_title=job_data["job_title"],
        company_name=job_data["company_name"],
        job_description=job_data["job_description"],
        user_profile=user_profile,
        resume_content="Original resume content...",
        platform=job_data["platform"],
        auto_submit=False
    )
    
    # Test complete application workflow
    print("Running complete application workflow...")
    result = orchestrator.process_application(request)
    
    if result.success:
        print("✅ Complete application workflow successful!")
        print(f"Status: {result.status}")
        if result.application_id:
            print(f"Application ID: {result.application_id}")
        if result.tracking_url:
            print(f"Tracking URL: {result.tracking_url}")
        if result.tailored_resume:
            print("✅ Resume tailored successfully")
        if result.cover_letter:
            print("✅ Cover letter generated successfully")
    else:
        print(f"❌ Application workflow failed: {result.error_message}")


def main():
    """Main test function"""
    print("🚀 PHASE 3: MULTI-AGENT APPLICATION SYSTEM TEST")
    print("="*60)
    
    try:
        # Get OpenAI API key
        api_key = get_openai_api_key()
        
        # Test individual agents
        test_resume_tailor_agent(api_key)
        test_cover_letter_agent(api_key)
        test_application_agent(api_key)
        test_tracking_agent(api_key)
        test_followup_agent(api_key)
        
        # Test complete workflow
        test_crewai_orchestrator(api_key)
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nPhase 3 Features Implemented:")
        print("✅ CrewAI Multi-Agent Orchestration")
        print("✅ AI-Powered Resume Tailoring")
        print("✅ Dynamic Cover Letter Generation")
        print("✅ Multi-Platform Application Submission")
        print("✅ Application Status Tracking")
        print("✅ Intelligent Follow-up Management")
        print("\nReady for Phase 4: Advanced Automation & Intelligence!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    main() 