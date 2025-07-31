"""
Skills Matcher Agent - Phase 2 AI Component

This agent uses vector embeddings and semantic similarity to match:
- User skills with job requirements
- Skill similarity and alternatives
- Skill gap analysis
- Learning recommendations
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SkillMatch:
    """Individual skill match result"""
    user_skill: str
    job_skill: str
    similarity_score: float
    is_match: bool
    confidence: float

@dataclass
class SkillsMatchResult:
    """Complete skills matching result"""
    user_skills: List[str]
    job_required_skills: List[str]
    job_preferred_skills: List[str]
    skill_matches: List[SkillMatch]
    overall_match_score: float
    required_skills_covered: float
    preferred_skills_covered: float
    missing_skills: List[str]
    skill_gaps: List[Dict[str, Any]]
    learning_recommendations: List[str]

class SkillsMatcherAgent:
    """AI agent for matching user skills with job requirements"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the skills matcher agent"""
        self.model_name = model_name
        
        # Load sentence transformer model
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
        
        # Skill similarity thresholds
        self.match_threshold = 0.7
        self.high_confidence_threshold = 0.85
        
        # Common skill variations and synonyms
        self.skill_synonyms = {
            "python": ["python programming", "python development", "python coding"],
            "javascript": ["js", "javascript programming", "javascript development"],
            "react": ["react.js", "reactjs", "react development"],
            "node.js": ["nodejs", "node", "node.js development"],
            "aws": ["amazon web services", "aws cloud", "amazon aws"],
            "docker": ["docker containers", "dockerization", "containerization"],
            "kubernetes": ["k8s", "kubernetes orchestration", "container orchestration"],
            "postgresql": ["postgres", "postgresql database", "postgres db"],
            "mysql": ["mysql database", "mysql db", "mysql development"],
            "mongodb": ["mongo", "mongodb database", "nosql"],
            "git": ["git version control", "git development", "version control"],
            "agile": ["agile methodology", "agile development", "scrum"],
            "scrum": ["scrum methodology", "agile scrum", "scrum development"],
            "machine learning": ["ml", "machine learning algorithms", "ai/ml"],
            "data science": ["data analysis", "data analytics", "data scientist"],
            "devops": ["devops engineering", "devops practices", "ci/cd"],
            "api": ["rest api", "api development", "web services"],
            "microservices": ["microservice architecture", "microservices development"],
            "sql": ["sql database", "sql programming", "database queries"]
        }
        
        logger.info("SkillsMatcherAgent initialized successfully")
    
    def match_skills(self, 
                    user_skills: List[str], 
                    job_required_skills: List[str],
                    job_preferred_skills: Optional[List[str]] = None) -> SkillsMatchResult:
        """
        Match user skills with job requirements
        
        Args:
            user_skills: List of user's skills
            job_required_skills: List of required job skills
            job_preferred_skills: List of preferred job skills
            
        Returns:
            SkillsMatchResult with comprehensive matching analysis
        """
        try:
            logger.info(f"Matching {len(user_skills)} user skills with {len(job_required_skills)} required skills")
            
            # Normalize skills
            normalized_user_skills = self._normalize_skills(user_skills)
            normalized_required_skills = self._normalize_skills(job_required_skills)
            normalized_preferred_skills = self._normalize_skills(job_preferred_skills or [])
            
            # Get embeddings
            user_embeddings = self.model.encode(normalized_user_skills)
            required_embeddings = self.model.encode(normalized_required_skills)
            preferred_embeddings = self.model.encode(normalized_preferred_skills) if normalized_preferred_skills else np.array([])
            
            # Calculate similarities
            required_similarities = cosine_similarity(user_embeddings, required_embeddings)
            preferred_similarities = cosine_similarity(user_embeddings, preferred_embeddings) if len(preferred_embeddings) > 0 else np.array([])
            
            # Find matches
            skill_matches = []
            
            # Match required skills
            for i, user_skill in enumerate(normalized_user_skills):
                for j, job_skill in enumerate(normalized_required_skills):
                    similarity = required_similarities[i][j]
                    is_match = similarity >= self.match_threshold
                    confidence = min(similarity * 1.2, 1.0)  # Boost confidence slightly
                    
                    skill_matches.append(SkillMatch(
                        user_skill=user_skills[i],  # Original skill name
                        job_skill=job_required_skills[j],  # Original job skill name
                        similarity_score=similarity,
                        is_match=is_match,
                        confidence=confidence
                    ))
            
            # Match preferred skills
            if len(preferred_similarities) > 0:
                for i, user_skill in enumerate(normalized_user_skills):
                    for j, job_skill in enumerate(normalized_preferred_skills):
                        similarity = preferred_similarities[i][j]
                        is_match = similarity >= self.match_threshold
                        confidence = min(similarity * 1.1, 1.0)  # Slightly lower confidence for preferred
                        
                        skill_matches.append(SkillMatch(
                            user_skill=user_skills[i],
                            job_skill=job_preferred_skills[j],
                            similarity_score=similarity,
                            is_match=is_match,
                            confidence=confidence
                        ))
            
            # Calculate overall metrics
            overall_match_score = self._calculate_overall_match_score(skill_matches, len(job_required_skills))
            required_skills_covered = self._calculate_skills_covered(skill_matches, job_required_skills, is_required=True)
            preferred_skills_covered = self._calculate_skills_covered(skill_matches, job_preferred_skills, is_required=False)
            
            # Identify missing skills
            missing_skills = self._identify_missing_skills(skill_matches, job_required_skills, job_preferred_skills)
            
            # Analyze skill gaps
            skill_gaps = self._analyze_skill_gaps(missing_skills, user_skills)
            
            # Generate learning recommendations
            learning_recommendations = self._generate_learning_recommendations(skill_gaps, missing_skills)
            
            result = SkillsMatchResult(
                user_skills=user_skills,
                job_required_skills=job_required_skills,
                job_preferred_skills=job_preferred_skills or [],
                skill_matches=skill_matches,
                overall_match_score=overall_match_score,
                required_skills_covered=required_skills_covered,
                preferred_skills_covered=preferred_skills_covered,
                missing_skills=missing_skills,
                skill_gaps=skill_gaps,
                learning_recommendations=learning_recommendations
            )
            
            logger.info(f"Skills matching completed. Overall score: {overall_match_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error matching skills: {str(e)}")
            raise
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skill names for better matching"""
        normalized = []
        
        for skill in skills:
            # Convert to lowercase
            skill_lower = skill.lower().strip()
            
            # Check for synonyms
            normalized_skill = skill_lower
            for main_skill, synonyms in self.skill_synonyms.items():
                if skill_lower in synonyms or skill_lower == main_skill:
                    normalized_skill = main_skill
                    break
            
            normalized.append(normalized_skill)
        
        return normalized
    
    def _calculate_overall_match_score(self, skill_matches: List[SkillMatch], total_required: int) -> float:
        """Calculate overall match score"""
        if total_required == 0:
            return 0.0
        
        # Get best matches for each required skill
        required_matches = [m for m in skill_matches if m.job_skill in [m.job_skill for m in skill_matches[:total_required]]]
        
        if not required_matches:
            return 0.0
        
        # Calculate weighted average
        total_score = sum(match.similarity_score for match in required_matches)
        return min(total_score / total_required, 1.0)
    
    def _calculate_skills_covered(self, skill_matches: List[SkillMatch], job_skills: List[str], is_required: bool = True) -> float:
        """Calculate percentage of skills covered"""
        if not job_skills:
            return 0.0
        
        covered_skills = set()
        for match in skill_matches:
            if match.is_match and match.job_skill in job_skills:
                covered_skills.add(match.job_skill)
        
        return len(covered_skills) / len(job_skills)
    
    def _identify_missing_skills(self, skill_matches: List[SkillMatch], required_skills: List[str], preferred_skills: List[str]) -> List[str]:
        """Identify skills that are not matched"""
        matched_skills = set()
        for match in skill_matches:
            if match.is_match:
                matched_skills.add(match.job_skill)
        
        all_job_skills = set(required_skills + preferred_skills)
        missing_skills = list(all_job_skills - matched_skills)
        
        return missing_skills
    
    def _analyze_skill_gaps(self, missing_skills: List[str], user_skills: List[str]) -> List[Dict[str, Any]]:
        """Analyze skill gaps and provide insights"""
        skill_gaps = []
        
        for missing_skill in missing_skills:
            # Find similar skills the user has
            similar_skills = self._find_similar_skills(missing_skill, user_skills)
            
            skill_gaps.append({
                "missing_skill": missing_skill,
                "similar_user_skills": similar_skills,
                "difficulty_level": self._assess_skill_difficulty(missing_skill),
                "learning_time_estimate": self._estimate_learning_time(missing_skill),
                "priority": "high" if missing_skill in ["python", "javascript", "sql"] else "medium"
            })
        
        return skill_gaps
    
    def _find_similar_skills(self, target_skill: str, user_skills: List[str]) -> List[str]:
        """Find skills similar to the target skill"""
        if not user_skills:
            return []
        
        # Get embeddings
        target_embedding = self.model.encode([target_skill.lower()])
        user_embeddings = self.model.encode([skill.lower() for skill in user_skills])
        
        # Calculate similarities
        similarities = cosine_similarity(target_embedding, user_embeddings)[0]
        
        # Find skills with similarity > 0.5
        similar_skills = []
        for i, similarity in enumerate(similarities):
            if similarity > 0.5:
                similar_skills.append(user_skills[i])
        
        return similar_skills
    
    def _assess_skill_difficulty(self, skill: str) -> str:
        """Assess the difficulty level of learning a skill"""
        skill_lower = skill.lower()
        
        # Easy skills (basic concepts)
        easy_skills = ["git", "html", "css", "agile", "scrum"]
        
        # Medium skills (moderate complexity)
        medium_skills = ["javascript", "python", "sql", "docker", "api"]
        
        # Hard skills (advanced concepts)
        hard_skills = ["machine learning", "kubernetes", "microservices", "devops", "data science"]
        
        if skill_lower in easy_skills:
            return "easy"
        elif skill_lower in medium_skills:
            return "medium"
        elif skill_lower in hard_skills:
            return "hard"
        else:
            return "medium"  # Default
    
    def _estimate_learning_time(self, skill: str) -> str:
        """Estimate time to learn a skill"""
        difficulty = self._assess_skill_difficulty(skill)
        
        if difficulty == "easy":
            return "1-2 weeks"
        elif difficulty == "medium":
            return "1-3 months"
        else:
            return "3-6 months"
    
    def _generate_learning_recommendations(self, skill_gaps: List[Dict[str, Any]], missing_skills: List[str]) -> List[str]:
        """Generate learning recommendations based on skill gaps"""
        recommendations = []
        
        # Prioritize high-priority skills
        high_priority_gaps = [gap for gap in skill_gaps if gap["priority"] == "high"]
        
        for gap in high_priority_gaps[:3]:  # Top 3 recommendations
            skill = gap["missing_skill"]
            difficulty = gap["difficulty_level"]
            time_estimate = gap["learning_time_estimate"]
            
            recommendation = f"Learn {skill} ({difficulty} difficulty, {time_estimate} estimated time)"
            if gap["similar_user_skills"]:
                recommendation += f" - You already know similar skills: {', '.join(gap['similar_user_skills'])}"
            
            recommendations.append(recommendation)
        
        # Add general recommendations
        if len(missing_skills) > 3:
            recommendations.append(f"Focus on the top {len(high_priority_gaps)} skills first")
        
        if not recommendations:
            recommendations.append("Great job! Your skills align well with the job requirements.")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Example skills
    user_skills = ["Python", "Django", "PostgreSQL", "Git", "HTML", "CSS"]
    job_required_skills = ["Python", "JavaScript", "React", "Node.js", "MongoDB"]
    job_preferred_skills = ["Docker", "AWS", "Machine Learning"]
    
    # Initialize matcher
    matcher = SkillsMatcherAgent()
    
    # Match skills
    result = matcher.match_skills(user_skills, job_required_skills, job_preferred_skills)
    
    print(f"Overall match score: {result.overall_match_score:.2f}")
    print(f"Required skills covered: {result.required_skills_covered:.2f}")
    print(f"Preferred skills covered: {result.preferred_skills_covered:.2f}")
    print(f"Missing skills: {result.missing_skills}")
    print(f"Learning recommendations: {result.learning_recommendations}") 