"""
CrewAI Agents for Intelligent Job Finder Phase 3

This module contains specialized agents for automated job application processes:
- Resume Tailor Agent
- Cover Letter Agent  
- Application Agent
- Tracking Agent
- Follow-up Agent
"""

from .orchestrator import ApplicationOrchestrator
from .resume_tailor import ResumeTailorAgent
from .cover_letter import CoverLetterAgent
from .application_agent import ApplicationAgent
from .tracking_agent import TrackingAgent
from .followup_agent import FollowupAgent

__all__ = [
    "ApplicationOrchestrator",
    "ResumeTailorAgent", 
    "CoverLetterAgent",
    "ApplicationAgent",
    "TrackingAgent",
    "FollowupAgent"
] 