"""
Follow-up Agent - Application follow-up management

This agent manages follow-up communications for job applications,
including timing, content generation, and response tracking.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class FollowupRequest:
    """Request structure for follow-up management"""
    application_id: str
    company_name: str
    job_title: str
    application_date: datetime
    followup_type: str = "standard"  # 'standard', 'aggressive', 'polite', 'custom'
    custom_message: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None


@dataclass
class FollowupResult:
    """Result structure for follow-up management"""
    success: bool
    followup_id: Optional[str] = None
    followup_message: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    followup_type: Optional[str] = None
    error_message: Optional[str] = None


class FollowupAgent:
    """
    Follow-up management agent for job applications.
    
    Features:
    - Intelligent follow-up timing
    - Personalized follow-up messages
    - Multiple follow-up strategies
    - Response tracking
    - Contact management
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4"):
        """
        Initialize the follow-up agent.
        
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
        
        # Follow-up timing guidelines
        self.timing_guidelines = {
            "standard": 7,      # 7 days after application
            "aggressive": 3,    # 3 days after application
            "polite": 10,       # 10 days after application
            "custom": 7         # Default to 7 days
        }
        
        # Follow-up strategies
        self.followup_strategies = {
            "standard": self._get_standard_strategy(),
            "aggressive": self._get_aggressive_strategy(),
            "polite": self._get_polite_strategy()
        }
        
        logger.info("FollowupAgent initialized successfully")
    
    def _get_standard_strategy(self) -> str:
        """Get standard follow-up strategy"""
        return """Use a professional, balanced approach that shows interest without being pushy.
        Focus on expressing continued interest and asking about the status of the application."""
    
    def _get_aggressive_strategy(self) -> str:
        """Get aggressive follow-up strategy"""
        return """Use a more assertive approach that demonstrates high interest and urgency.
        Emphasize qualifications and readiness to move forward quickly."""
    
    def _get_polite_strategy(self) -> str:
        """Get polite follow-up strategy"""
        return """Use a gentle, respectful approach that acknowledges the hiring team's busy schedule.
        Express gratitude for the opportunity and ask politely about the status."""
    
    def schedule_followup(self, application_id: str, followup_type: str = "standard") -> bool:
        """
        Schedule a follow-up for an application.
        
        Args:
            application_id: Application ID
            followup_type: Type of follow-up strategy
            
        Returns:
            True if follow-up was scheduled successfully
        """
        try:
            days_to_wait = self.timing_guidelines.get(followup_type, 7)
            scheduled_date = datetime.now() + timedelta(days=days_to_wait)
            
            logger.info(f"Follow-up scheduled for application {application_id} on {scheduled_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling follow-up: {str(e)}")
            return False
    
    def generate_followup_message(self, request: FollowupRequest) -> FollowupResult:
        """
        Generate a personalized follow-up message.
        
        Args:
            request: FollowupRequest with all necessary information
            
        Returns:
            FollowupResult with generated message
        """
        try:
            logger.info(f"Generating follow-up message for {request.application_id}")
            
            # Calculate days since application
            days_since_application = (datetime.now() - request.application_date).days
            
            # Get strategy
            strategy = self.followup_strategies.get(request.followup_type, self.followup_strategies["standard"])
            
            # Generate message
            if request.custom_message:
                message = self._customize_message(request.custom_message, request)
            else:
                message = self._generate_standard_message(request, strategy, days_since_application)
            
            # Generate follow-up ID
            followup_id = f"followup_{request.application_id}_{datetime.now().strftime('%Y%m%d')}"
            
            # Calculate scheduled date
            days_to_wait = self.timing_guidelines.get(request.followup_type, 7)
            scheduled_date = request.application_date + timedelta(days=days_to_wait)
            
            result = FollowupResult(
                success=True,
                followup_id=followup_id,
                followup_message=message,
                scheduled_date=scheduled_date,
                followup_type=request.followup_type
            )
            
            logger.info(f"Follow-up message generated successfully. ID: {followup_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating follow-up message: {str(e)}")
            return FollowupResult(
                success=False,
                error_message=str(e)
            )
    
    def _generate_standard_message(self, request: FollowupRequest, strategy: str, 
                                 days_since_application: int) -> str:
        """
        Generate a standard follow-up message.
        
        Args:
            request: Follow-up request
            strategy: Follow-up strategy
            days_since_application: Days since application was submitted
            
        Returns:
            Generated follow-up message
        """
        prompt = f"""
        Generate a professional follow-up message for a job application.
        
        {strategy}
        
        Application Details:
        - Company: {request.company_name}
        - Job Title: {request.job_title}
        - Days Since Application: {days_since_application}
        - Application ID: {request.application_id}
        
        Contact Information: {request.contact_info or 'Not provided'}
        
        The message should:
        1. Be professional and courteous
        2. Reference the specific job and company
        3. Express continued interest
        4. Ask about the application status
        5. Provide contact information
        6. Be concise (150-200 words)
        7. Match the specified strategy tone
        
        Generate a complete follow-up message.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def _customize_message(self, base_message: str, request: FollowupRequest) -> str:
        """
        Customize a base message for the specific application.
        
        Args:
            base_message: Base message to customize
            request: Follow-up request
            
        Returns:
            Customized message
        """
        prompt = f"""
        Customize this follow-up message for the specific application.
        
        Base Message:
        {base_message}
        
        Application Details:
        - Company: {request.company_name}
        - Job Title: {request.job_title}
        - Application ID: {request.application_id}
        
        Customize the message to:
        1. Include the specific company and job title
        2. Maintain the original tone and style
        3. Add personal touches relevant to this application
        4. Ensure it's professional and appropriate
        
        Return the customized message.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def determine_followup_timing(self, application_date: datetime, 
                                company_type: str = "standard") -> datetime:
        """
        Determine optimal follow-up timing based on company type and application date.
        
        Args:
            application_date: Date when application was submitted
            company_type: Type of company ('startup', 'corporate', 'agency', 'standard')
            
        Returns:
            Optimal follow-up date
        """
        try:
            # Different timing for different company types
            timing_rules = {
                "startup": 3,      # Startups move faster
                "corporate": 10,   # Corporations take longer
                "agency": 5,       # Agencies are in between
                "standard": 7      # Default timing
            }
            
            days_to_wait = timing_rules.get(company_type, 7)
            optimal_date = application_date + timedelta(days=days_to_wait)
            
            return optimal_date
            
        except Exception as e:
            logger.error(f"Error determining follow-up timing: {str(e)}")
            return application_date + timedelta(days=7)
    
    def track_followup_response(self, followup_id: str, response_received: bool = False, 
                              response_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Track follow-up responses and determine next actions.
        
        Args:
            followup_id: ID of the follow-up
            response_received: Whether a response was received
            response_content: Content of the response if received
            
        Returns:
            Dictionary with tracking information and next actions
        """
        try:
            tracking_info = {
                "followup_id": followup_id,
                "response_received": response_received,
                "response_date": datetime.now().isoformat() if response_received else None,
                "next_action": "wait" if not response_received else "analyze_response"
            }
            
            if response_received and response_content:
                # Analyze response content
                analysis = self._analyze_response(response_content)
                tracking_info["response_analysis"] = analysis
                
                # Determine next action based on response
                if "interview" in response_content.lower():
                    tracking_info["next_action"] = "prepare_for_interview"
                elif "reject" in response_content.lower() or "not selected" in response_content.lower():
                    tracking_info["next_action"] = "move_on"
                else:
                    tracking_info["next_action"] = "wait_for_further_communication"
            
            return tracking_info
            
        except Exception as e:
            logger.error(f"Error tracking follow-up response: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_response(self, response_content: str) -> Dict[str, Any]:
        """
        Analyze the content of a follow-up response.
        
        Args:
            response_content: Content of the response
            
        Returns:
            Dictionary with analysis results
        """
        try:
            prompt = f"""
            Analyze this follow-up response from a company.
            
            Response:
            {response_content}
            
            Provide analysis on:
            1. Response type (positive, negative, neutral, informational)
            2. Key information provided
            3. Next steps mentioned
            4. Timeline provided
            5. Overall sentiment
            
            Return a brief analysis.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return {"analysis": response.content}
            
        except Exception as e:
            logger.error(f"Error analyzing response: {str(e)}")
            return {"analysis": "Unable to analyze response"}
    
    def generate_multiple_followups(self, application_id: str, company_name: str, 
                                  job_title: str, application_date: datetime) -> List[FollowupResult]:
        """
        Generate multiple follow-up messages with different strategies.
        
        Args:
            application_id: Application ID
            company_name: Company name
            job_title: Job title
            application_date: Application date
            
        Returns:
            List of follow-up results with different strategies
        """
        try:
            results = []
            strategies = ["standard", "aggressive", "polite"]
            
            for strategy in strategies:
                request = FollowupRequest(
                    application_id=application_id,
                    company_name=company_name,
                    job_title=job_title,
                    application_date=application_date,
                    followup_type=strategy
                )
                
                result = self.generate_followup_message(request)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating multiple follow-ups: {str(e)}")
            return [] 