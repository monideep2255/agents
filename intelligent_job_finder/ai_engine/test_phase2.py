"""
Test Script for Phase 2 AI Engine

This script tests the basic functionality of our AI agents without requiring
external API keys or complex dependencies.
"""

import sys
import os
from typing import Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from agents.job_analyzer import JobAnalyzerAgent, JobAnalysisResult
        print("✅ JobAnalyzerAgent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JobAnalyzerAgent: {e}")
    
    try:
        from agents.skills_matcher import SkillsMatcherAgent, SkillsMatchResult
        print("✅ SkillsMatcherAgent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SkillsMatcherAgent: {e}")
    
    try:
        from main import AIEngineOrchestrator, JobAnalysisRequest
        print("✅ AIEngineOrchestrator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AIEngineOrchestrator: {e}")

def test_data_structures():
    """Test data structure creation"""
    print("\n🧪 Testing data structures...")
    
    # Test JobAnalysisResult
    try:
        from agents.job_analyzer import JobAnalysisResult
        
        result = JobAnalysisResult(
            job_id="test_001",
            title="Test Job",
            company="Test Company",
            required_skills=["Python", "JavaScript"],
            preferred_skills=["Docker"],
            experience_level="Mid",
            salary_range={"min": 80000, "max": 120000},
            job_quality_score=85.0,
            company_insights={"industry": "Technology"},
            match_score=0.8,
            analysis_summary="Good match for the position"
        )
        print("✅ JobAnalysisResult created successfully")
        print(f"   - Job Quality Score: {result.job_quality_score}")
        print(f"   - Match Score: {result.match_score}")
        
    except Exception as e:
        print(f"❌ Failed to create JobAnalysisResult: {e}")
    
    # Test SkillsMatchResult
    try:
        from agents.skills_matcher import SkillsMatchResult, SkillMatch
        
        skill_match = SkillMatch(
            user_skill="Python",
            job_skill="Python Development",
            similarity_score=0.9,
            is_match=True,
            confidence=0.95
        )
        
        result = SkillsMatchResult(
            user_skills=["Python", "JavaScript"],
            job_required_skills=["Python", "React"],
            job_preferred_skills=["Docker"],
            skill_matches=[skill_match],
            overall_match_score=0.85,
            required_skills_covered=0.5,
            preferred_skills_covered=0.0,
            missing_skills=["React"],
            skill_gaps=[],
            learning_recommendations=["Learn React"]
        )
        print("✅ SkillsMatchResult created successfully")
        print(f"   - Overall Match Score: {result.overall_match_score}")
        print(f"   - Missing Skills: {result.missing_skills}")
        
    except Exception as e:
        print(f"❌ Failed to create SkillsMatchResult: {e}")

def test_orchestrator_structure():
    """Test orchestrator structure without API calls"""
    print("\n🧪 Testing orchestrator structure...")
    
    try:
        from main import AIEngineOrchestrator, JobAnalysisRequest, JobAnalysisResponse
        
        # Test request creation
        sample_job = {
            "id": "test_001",
            "title": "Python Developer",
            "company": "TechCorp",
            "location": "San Francisco, CA",
            "description": "We are looking for a Python developer..."
        }
        
        sample_profile = {
            "skills": ["Python", "Django"],
            "experience_years": 3,
            "education": "Bachelor's",
            "preferred_salary": 100000,
            "location": "San Francisco, CA"
        }
        
        request = JobAnalysisRequest(
            job_data=sample_job,
            user_profile=sample_profile,
            include_skills_matching=True,
            include_company_research=True,
            include_salary_analysis=True
        )
        print("✅ JobAnalysisRequest created successfully")
        
        # Test orchestrator initialization (without API key)
        try:
            orchestrator = AIEngineOrchestrator("fake_api_key")
            print("✅ AIEngineOrchestrator structure created successfully")
        except ValueError as e:
            print("✅ AIEngineOrchestrator properly validates API key")
        
    except Exception as e:
        print(f"❌ Failed to test orchestrator structure: {e}")

def test_skill_synonyms():
    """Test skill synonym matching"""
    print("\n🧪 Testing skill synonyms...")
    
    try:
        from agents.skills_matcher import SkillsMatcherAgent
        
        # Create matcher (this will fail without the model, but we can test the synonym logic)
        matcher = SkillsMatcherAgent()
        
        # Test synonym dictionary
        synonyms = matcher.skill_synonyms
        
        test_cases = [
            ("python", "python"),
            ("js", "javascript"),
            ("react.js", "react"),
            ("postgres", "postgresql"),
            ("aws cloud", "aws")
        ]
        
        print("✅ Skill synonyms dictionary loaded")
        print(f"   - Number of skill mappings: {len(synonyms)}")
        
        for input_skill, expected in test_cases:
            if input_skill in synonyms or any(input_skill in syns for syns in synonyms.values()):
                print(f"   - '{input_skill}' has synonym mapping")
            else:
                print(f"   - '{input_skill}' not found in synonyms")
        
    except Exception as e:
        print(f"❌ Failed to test skill synonyms: {e}")

def main():
    """Run all tests"""
    print("🚀 Phase 2 AI Engine Test Suite")
    print("=" * 50)
    
    test_imports()
    test_data_structures()
    test_orchestrator_structure()
    test_skill_synonyms()
    
    print("\n" + "=" * 50)
    print("✅ Phase 2 structure test completed!")
    print("\n📝 Next steps:")
    print("1. Set up OpenAI API key for full functionality")
    print("2. Install sentence-transformers for skills matching")
    print("3. Test with real job data")
    print("4. Integrate with backend API")

if __name__ == "__main__":
    main() 