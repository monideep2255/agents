# Intelligent Job Finder & Auto-Applicator
## Development Guide

### Version: 1.0
### Date: July 2025
### Author: AI Agents Course Project

---

## 1. Development Environment Setup

### 1.1 Prerequisites
```bash
# Required Software
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose
- Git

# Python Dependencies
- pip
- virtualenv or conda
- poetry (recommended)

# Development Tools
- VS Code or PyCharm
- Postman or Insomnia
- pgAdmin or DBeaver
```

### 1.2 Project Structure
```
intelligent_job_finder/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── ai_engine/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── job_scout.py
│   │   ├── resume_tailor.py
│   │   ├── cover_letter.py
│   │   └── application_submitter.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── job_search_workflow.py
│   │   └── application_workflow.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── job_board_tools.py
│   │   ├── linkedin_tools.py
│   │   └── email_tools.py
│   └── requirements.txt
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── README.md
├── PRD.md
├── TECHNICAL_SPEC.md
└── DEVELOPMENT_GUIDE.md
```

### 1.3 Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd intelligent_job_finder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r ai_engine/requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Database setup
docker-compose up -d postgres redis
```

---

## 2. Development Principles

### 2.1 Code Quality Standards

#### 2.1.1 Python Code Style
```python
# Follow PEP 8 standards
# Use type hints
# Maximum line length: 88 characters (Black formatter)
# Use meaningful variable names

# Example of good code style
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class JobApplication(BaseModel):
    """Represents a job application."""
    
    user_id: str
    job_id: str
    resume_version: str
    cover_letter: Optional[str] = None
    applied_date: datetime = datetime.now()
    
    def is_recent(self, days: int = 7) -> bool:
        """Check if application was submitted within specified days."""
        return (datetime.now() - self.applied_date).days <= days
```

#### 2.1.2 TypeScript Code Style
```typescript
// Follow ESLint and Prettier configurations
// Use strict TypeScript settings
// Prefer interfaces over types for object shapes
// Use meaningful variable names

// Example of good code style
interface JobApplication {
  userId: string;
  jobId: string;
  resumeVersion: string;
  coverLetter?: string;
  appliedDate: Date;
}

class ApplicationService {
  private readonly apiClient: ApiClient;
  
  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }
  
  async submitApplication(application: JobApplication): Promise<void> {
    try {
      await this.apiClient.post('/applications', application);
    } catch (error) {
      throw new ApplicationError('Failed to submit application', error);
    }
  }
}
```

### 2.2 Modular Architecture

#### 2.2.1 Backend Modularity
```python
# Each module should be self-contained
# Use dependency injection
# Follow SOLID principles

# Example: Service Layer
class JobService:
    def __init__(self, job_repository: JobRepository, ai_service: AIService):
        self.job_repository = job_repository
        self.ai_service = ai_service
    
    async def search_jobs(self, criteria: JobSearchCriteria) -> List[Job]:
        """Search for jobs based on criteria."""
        jobs = await self.job_repository.search(criteria)
        return await self.ai_service.rank_jobs(jobs, criteria)

# Example: Repository Pattern
class JobRepository:
    def __init__(self, database: Database):
        self.database = database
    
    async def search(self, criteria: JobSearchCriteria) -> List[Job]:
        """Search jobs in database."""
        query = self._build_search_query(criteria)
        return await self.database.execute(query)
```

#### 2.2.2 Frontend Modularity
```typescript
// Use component-based architecture
// Separate concerns (UI, business logic, data)
// Use custom hooks for reusable logic

// Example: Custom Hook
export const useJobSearch = (criteria: JobSearchCriteria) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const searchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const results = await jobService.search(criteria);
      setJobs(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [criteria]);
  
  return { jobs, loading, error, searchJobs };
};

// Example: Component
export const JobSearchComponent: React.FC = () => {
  const { jobs, loading, error, searchJobs } = useJobSearch(criteria);
  
  return (
    <div>
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {jobs.map(job => <JobCard key={job.id} job={job} />)}
    </div>
  );
};
```

### 2.3 Scalability Guidelines

#### 2.3.1 Database Design
```sql
-- Use proper indexing
-- Implement pagination
-- Use connection pooling
-- Consider read replicas for scaling

-- Example: Proper indexing
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_salary ON jobs(salary_min, salary_max);
CREATE INDEX idx_applications_user_date ON applications(user_id, applied_date);

-- Example: Pagination query
SELECT * FROM jobs 
WHERE location = 'San Francisco' 
ORDER BY posted_date DESC 
LIMIT 20 OFFSET 40;
```

#### 2.3.2 Caching Strategy
```python
# Use Redis for caching
# Implement cache invalidation
# Use appropriate TTL values

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def get_job_recommendations(self, user_id: str) -> List[Job]:
        """Get cached job recommendations."""
        cache_key = f"recommendations:{user_id}"
        cached = await self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        recommendations = await self._generate_recommendations(user_id)
        await self.redis.setex(cache_key, 3600, json.dumps(recommendations))
        return recommendations
```

---

## 3. AI Agent Development Guidelines

### 3.1 Agent Design Principles

#### 3.1.1 Single Responsibility
```python
# Each agent should have one clear purpose
# Keep agents focused and specialized

class JobScoutAgent:
    """Agent responsible for finding relevant jobs."""
    
    def __init__(self, llm: ChatOpenAI, tools: List[Tool]):
        self.llm = llm
        self.tools = tools
    
    async def search_jobs(self, criteria: JobSearchCriteria) -> List[Job]:
        """Search for jobs based on criteria."""
        # Only handle job search logic
        pass
    
    async def filter_jobs(self, jobs: List[Job], preferences: Dict) -> List[Job]:
        """Filter jobs based on user preferences."""
        # Only handle job filtering logic
        pass
```

#### 3.1.2 Error Handling
```python
# Implement robust error handling
# Provide meaningful error messages
# Log errors for debugging

class AIService:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    async def process_with_retry(self, func: Callable, max_retries: int = 3):
        """Execute function with retry logic."""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 3.2 Workflow Management

#### 3.2.1 LangGraph Workflow Design
```python
# Design workflows as state machines
# Use clear state transitions
# Implement proper error handling

class ApplicationWorkflow:
    def __init__(self):
        self.workflow = StateGraph(ApplicationState)
        self._setup_nodes()
        self._setup_edges()
    
    def _setup_nodes(self):
        """Setup workflow nodes."""
        self.workflow.add_node("search_jobs", self.search_jobs_node)
        self.workflow.add_node("analyze_jobs", self.analyze_jobs_node)
        self.workflow.add_node("tailor_resume", self.tailor_resume_node)
        self.workflow.add_node("submit_application", self.submit_application_node)
    
    def _setup_edges(self):
        """Setup workflow edges."""
        self.workflow.add_edge("search_jobs", "analyze_jobs")
        self.workflow.add_conditional_edges(
            "analyze_jobs",
            self.should_apply_router,
            {"apply": "tailor_resume", "skip": "search_jobs"}
        )
        self.workflow.add_edge("tailor_resume", "submit_application")
```

#### 3.2.2 CrewAI Orchestration
```python
# Use CrewAI for complex multi-agent tasks
# Define clear task descriptions
# Monitor agent performance

class JobApplicationCrew:
    def __init__(self):
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        self.crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            memory=True
        )
    
    def _create_agents(self) -> List[Agent]:
        """Create specialized agents."""
        return [
            Agent(
                role="Job Scout",
                goal="Find the best job opportunities",
                backstory="Expert at discovering hidden job opportunities",
                tools=[WebSearchTool(), JobBoardAPITool()]
            ),
            Agent(
                role="Resume Tailor",
                goal="Optimize resumes for specific jobs",
                backstory="Resume optimization specialist",
                tools=[ResumeAnalysisTool(), ATSOptimizationTool()]
            )
        ]
```

### 3.3 Tool Integration

#### 3.3.1 MCP Tool Development
```python
# Follow MCP protocol standards
# Implement proper error handling
# Use async/await for I/O operations

class JobBoardMCPTool:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.name = "job_board_search"
        self.description = "Search job boards for positions"
    
    async def execute(self, query: str) -> List[Job]:
        """Execute job board search."""
        try {
            response = await self.api_client.search_jobs(query)
            return self._parse_jobs(response)
        } catch (error) {
            logger.error(f"Job board search failed: {e}")
            raise ToolExecutionError(f"Failed to search job boards: {e}")
    
    def _parse_jobs(self, response: Dict) -> List[Job]:
        """Parse API response into Job objects."""
        jobs = []
        for job_data in response.get("jobs", []):
            jobs.append(Job(**job_data))
        return jobs
```

---

## 4. Testing Strategy

### 4.1 Test Types and Coverage

#### 4.1.1 Unit Tests
```python
# Test individual functions and classes
# Mock external dependencies
# Aim for 90% code coverage

import pytest
from unittest.mock import Mock, patch

class TestJobService:
    def setup_method(self):
        self.mock_repository = Mock()
        self.mock_ai_service = Mock()
        self.service = JobService(self.mock_repository, self.mock_ai_service)
    
    async def test_search_jobs_success(self):
        """Test successful job search."""
        # Arrange
        criteria = JobSearchCriteria(keywords=["python", "ai"])
        expected_jobs = [Job(id="1", title="AI Engineer")]
        self.mock_repository.search.return_value = expected_jobs
        self.mock_ai_service.rank_jobs.return_value = expected_jobs
        
        # Act
        result = await self.service.search_jobs(criteria)
        
        # Assert
        assert result == expected_jobs
        self.mock_repository.search.assert_called_once_with(criteria)
```

#### 4.1.2 Integration Tests
```python
# Test component interactions
# Use test database
# Test API endpoints

class TestJobAPI:
    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_test_app()
        async with TestClient(app) as client:
            yield client
    
    async def test_search_jobs_endpoint(self, client):
        """Test job search API endpoint."""
        response = await client.get("/api/v1/jobs/search?keywords=python")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
```

#### 4.1.3 End-to-End Tests
```python
# Test complete user workflows
# Use real browser automation
# Test AI agent interactions

class TestJobApplicationWorkflow:
    async def test_complete_application_process(self):
        """Test complete job application workflow."""
        # Setup
        user = await create_test_user()
        job = await create_test_job()
        
        # Execute workflow
        workflow = ApplicationWorkflow()
        result = await workflow.run({
            "user_id": user.id,
            "job_id": job.id
        })
        
        # Verify results
        assert result["status"] == "completed"
        assert result["application_id"] is not None
```

### 4.2 AI Agent Testing

#### 4.2.1 Agent Behavior Testing
```python
# Test agent responses
# Validate tool usage
# Test error scenarios

class TestJobScoutAgent:
    async def test_job_search_behavior(self):
        """Test job scout agent behavior."""
        agent = JobScoutAgent(llm=MockLLM(), tools=[MockTool()])
        
        # Test successful search
        with patch.object(agent.tools[0], 'execute') as mock_execute:
            mock_execute.return_value = [Job(id="1", title="AI Engineer")]
            result = await agent.search_jobs({"keywords": ["python"]})
            
            assert len(result) == 1
            assert result[0].title == "AI Engineer"
            mock_execute.assert_called_once()
    
    async def test_agent_error_handling(self):
        """Test agent error handling."""
        agent = JobScoutAgent(llm=MockLLM(), tools=[MockTool()])
        
        # Test tool failure
        with patch.object(agent.tools[0], 'execute') as mock_execute:
            mock_execute.side_effect = Exception("API Error")
            
            with pytest.raises(AgentError):
                await agent.search_jobs({"keywords": ["python"]})
```

---

## 5. Performance Optimization

### 5.1 Database Optimization
```python
# Use proper indexing
# Implement query optimization
# Use connection pooling

# Example: Optimized query
async def get_user_applications(user_id: str, limit: int = 20) -> List[Application]:
    """Get user applications with pagination."""
    query = """
        SELECT a.*, j.title, j.company
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.user_id = :user_id
        ORDER BY a.applied_date DESC
        LIMIT :limit
    """
    return await database.fetch_all(
        query, 
        {"user_id": user_id, "limit": limit}
    )
```

### 5.2 Caching Strategy
```python
# Implement multi-level caching
# Use appropriate cache keys
# Implement cache invalidation

class CacheManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def get_or_set(self, key: str, func: Callable, ttl: int = 3600):
        """Get from cache or execute function and cache result."""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        result = await func()
        await self.redis.setex(key, ttl, json.dumps(result))
        return result
```

### 5.3 AI Processing Optimization
```python
# Implement request batching
# Use async processing
# Implement rate limiting

class AIServiceOptimizer:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
    
    async def batch_process(self, items: List[Any], batch_size: int = 10):
        """Process items in batches."""
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.process_item(item) for item in batch]
            )
            results.extend(batch_results)
        return results
```

---

## 6. Security Guidelines

### 6.1 Authentication & Authorization
```python
# Implement JWT authentication
# Use role-based access control
# Validate all inputs

class SecurityMiddleware:
    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret
    
    async def authenticate(self, token: str) -> Optional[User]:
        """Authenticate JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return await get_user_by_id(payload["user_id"])
        except jwt.InvalidTokenError:
            return None
    
    def authorize(self, user: User, resource: str, action: str) -> bool:
        """Check user permissions."""
        return user.has_permission(f"{resource}:{action}")
```

### 6.2 Data Protection
```python
# Encrypt sensitive data
# Implement data anonymization
# Follow GDPR requirements

class DataProtection:
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive user data."""
        cipher = AES.new(self.encryption_key.encode(), AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    
    def anonymize_user_data(self, user_data: Dict) -> Dict:
        """Anonymize user data for analytics."""
        return {
            "age_group": self._get_age_group(user_data["age"]),
            "location_region": self._get_region(user_data["location"]),
            "job_category": user_data["job_category"]
        }
```

---

## 7. Deployment Guidelines

### 7.1 Docker Configuration
```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Environment Configuration
```python
# Use environment variables for configuration
# Implement configuration validation
# Use different configs for different environments

class Config:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.redis_url = os.getenv("REDIS_URL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.jwt_secret = os.getenv("JWT_SECRET")
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration."""
        required_vars = [
            "DATABASE_URL", "REDIS_URL", 
            "OPENAI_API_KEY", "JWT_SECRET"
        ]
        
        missing_vars = [var for var in required_vars 
                       if not getattr(self, var.lower())]
        
        if missing_vars:
            raise ConfigurationError(f"Missing required environment variables: {missing_vars}")
```

### 7.3 Monitoring & Logging
```python
# Implement structured logging
# Use health checks
# Monitor application metrics

class MonitoringService:
    def __init__(self, logger: Logger, metrics: MetricsCollector):
        self.logger = logger
        self.metrics = metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        checks = {
            "database": await self._check_database(),
            "redis": await self._check_redis(),
            "ai_services": await self._check_ai_services()
        }
        
        overall_health = all(checks.values())
        self.metrics.health_status.set(1 if overall_health else 0)
        
        return {
            "status": "healthy" if overall_health else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
```

---

## 8. Code Review Guidelines

### 8.1 Review Checklist
- [ ] Code follows style guidelines
- [ ] Proper error handling implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] No hardcoded secrets or credentials

### 8.2 Review Process
1. **Self-Review**: Developer reviews their own code first
2. **Peer Review**: At least one peer reviews the code
3. **Automated Checks**: CI/CD pipeline runs tests and linting
4. **Final Approval**: Senior developer approves for merge

### 8.3 Code Review Comments
```python
# Good review comment
"""
Consider adding error handling for the case where the API returns an empty response.
This could happen if the job board is temporarily unavailable.
"""

# Bad review comment
"""
This is wrong.
"""
```

---

## 9. Documentation Standards

### 9.1 Code Documentation
```python
class JobService:
    """Service for managing job-related operations.
    
    This service handles job search, analysis, and application processes.
    It integrates with AI agents to provide intelligent job matching.
    """
    
    def __init__(self, repository: JobRepository, ai_service: AIService):
        """Initialize the job service.
        
        Args:
            repository: Repository for job data access
            ai_service: Service for AI-powered job analysis
        """
        self.repository = repository
        self.ai_service = ai_service
    
    async def search_jobs(self, criteria: JobSearchCriteria) -> List[Job]:
        """Search for jobs based on specified criteria.
        
        Args:
            criteria: Search criteria including keywords, location, salary range
            
        Returns:
            List of matching jobs
            
        Raises:
            JobSearchError: If search fails due to external API issues
            ValidationError: If search criteria are invalid
        """
        # Implementation here
        pass
```

### 9.2 API Documentation
```python
@router.get("/jobs/search", response_model=List[Job])
async def search_jobs(
    keywords: str = Query(..., description="Job keywords separated by commas"),
    location: Optional[str] = Query(None, description="Job location"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, description="Maximum salary"),
    current_user: User = Depends(get_current_user)
) -> List[Job]:
    """
    Search for jobs based on specified criteria.
    
    This endpoint searches multiple job boards and returns matching positions.
    Results are ranked using AI-powered matching algorithms.
    
    - **keywords**: Required. Job-related keywords (e.g., "python,ai,machine learning")
    - **location**: Optional. Job location (e.g., "San Francisco, CA")
    - **salary_min**: Optional. Minimum salary requirement
    - **salary_max**: Optional. Maximum salary expectation
    """
    # Implementation here
    pass
```

---

## 10. Development Workflow

### 10.1 Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/job-search-enhancement
# Make changes
git add .
git commit -m "feat: enhance job search with AI ranking"
git push origin feature/job-search-enhancement
# Create pull request
```

### 10.2 Commit Message Standards
```
feat: add AI-powered job ranking
fix: resolve job search pagination issue
docs: update API documentation
test: add unit tests for job service
refactor: improve error handling in AI agents
style: format code according to style guide
```

### 10.3 Branch Naming Convention
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions or improvements
- `refactor/` - Code refactoring
- `hotfix/` - Critical bug fixes

---

This development guide provides comprehensive guidelines for building the Intelligent Job Finder & Auto-Applicator system. Follow these standards to ensure code quality, maintainability, and scalability. 