# CLAUDE.md - OnCall Agent Project Guide

This document provides comprehensive guidance for AI assistants working on the OnCall Agent codebase. It covers the project structure, development workflows, and key conventions to follow.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Development Workflows](#development-workflows)
4. [Key Conventions](#key-conventions)
5. [Testing Strategy](#testing-strategy)
6. [Deployment & Operations](#deployment--operations)
7. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Overview

### Purpose
OnCall Agent is an intelligent system designed to handle on-call operations, incident management, and automated response workflows. The system uses AI/LLM capabilities to reduce the burden on human operators by automating common incident response patterns and providing intelligent assistance during critical situations.

### Key Capabilities
- **Incident Detection**: Monitor systems and detect anomalies/incidents using AI analysis
- **Alert Management**: Receive, prioritize, and intelligently route alerts
- **Automated Response**: Execute predefined runbooks and AI-assisted remediation steps
- **Escalation Logic**: Intelligent escalation based on severity, context, and response times
- **Communication**: Interface with chat platforms (Slack), ticketing systems (Jira), and paging services (PagerDuty)
- **Learning & Adaptation**: Learn from past incidents to improve responses over time

### Technology Stack
- **Language**: Python 3.11+ (primary language)
- **API Framework**: FastAPI (async, high-performance)
- **AI/LLM**: LangChain, LangGraph, OpenAI/Anthropic APIs
- **Database**: PostgreSQL (relational data), Redis (caching/queues)
- **ORM**: SQLAlchemy 2.0+ with async support
- **Task Queue**: Celery with Redis/RabbitMQ backend
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Kubernetes
- **CI/CD**: GitHub Actions

---

## Codebase Architecture

### Directory Structure

```
oncall-agent/
├── app/
│   ├── agent/               # Core agent logic
│   │   ├── brain.py        # Decision-making engine (LLM integration)
│   │   ├── memory.py       # State and context management
│   │   ├── tools.py        # Agent tools/actions
│   │   └── prompts/        # LLM prompts and templates
│   ├── integrations/        # External service integrations
│   │   ├── pagerduty/      # PagerDuty integration
│   │   ├── slack/          # Slack integration
│   │   ├── jira/           # Jira integration
│   │   └── monitoring/     # Prometheus, Datadog, etc.
│   ├── api/                 # FastAPI endpoints
│   │   ├── routes/         # Route definitions
│   │   ├── dependencies.py # Dependency injection
│   │   └── middleware.py   # Auth, validation, etc.
│   ├── services/            # Business logic layer
│   │   ├── incident.py     # Incident management
│   │   ├── alert.py        # Alert processing
│   │   ├── runbook.py      # Runbook execution
│   │   └── escalation.py   # Escalation logic
│   ├── models/              # SQLAlchemy models
│   │   ├── incident.py
│   │   ├── alert.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas for validation
│   │   ├── incident.py
│   │   ├── alert.py
│   │   └── user.py
│   ├── database/            # Database setup and migrations
│   │   ├── session.py      # Database session management
│   │   └── migrations/     # Alembic migrations
│   ├── workers/             # Celery background tasks
│   │   ├── alert_processor.py
│   │   └── health_check.py
│   ├── core/                # Core utilities
│   │   ├── config.py       # Configuration management
│   │   ├── logging.py      # Structured logging
│   │   ├── security.py     # Auth/security utilities
│   │   └── exceptions.py   # Custom exceptions
│   └── utils/               # Shared utilities
│       ├── retry.py        # Retry logic
│       └── cache.py        # Caching utilities
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── docs/                    # Additional documentation
│   ├── architecture.md
│   ├── api.md
│   └── runbooks/
├── scripts/                 # Utility scripts
├── alembic/                 # Database migrations
├── .github/
│   └── workflows/          # CI/CD pipelines
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements/
│   ├── base.txt           # Core dependencies
│   ├── dev.txt            # Development dependencies
│   └── prod.txt           # Production dependencies
├── pyproject.toml
├── pytest.ini
├── .env.example
└── CLAUDE.md              # This file
```

### Core Components

#### 1. Agent Brain (`app/agent/brain.py`)
The AI-powered decision-making engine that:
- Analyzes incoming alerts and incidents using LLMs
- Determines appropriate actions based on context and history
- Manages agent state and decision history
- Coordinates with external services
- Uses LangChain/LangGraph for agent orchestration

#### 2. Integrations (`app/integrations/`)
Each integration follows a standard protocol pattern:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class Integration(ABC):
    """Base integration interface"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the integration"""
        pass

    @abstractmethod
    async def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming event"""
        pass

    @abstractmethod
    async def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action"""
        pass
```

#### 3. Services Layer (`app/services/`)
Business logic that:
- Processes incidents through their lifecycle
- Executes runbooks and automated remediation
- Manages escalations and notifications
- Maintains audit logs
- Coordinates between integrations and the agent

#### 4. API Layer (`app/api/`)
FastAPI-based REST API with:
- Webhook receivers (alerts from monitoring systems)
- Configuration management endpoints
- Incident query and updates
- Admin operations
- Automatic OpenAPI/Swagger documentation

---

## Development Workflows

### Getting Started

```bash
# Clone the repository
git clone <repository-url>
cd oncall-agent

# Create virtual environment (recommended: Python 3.11+)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Set up database
alembic upgrade head

# Seed database (optional)
python scripts/seed_db.py

# Run in development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Individual feature branches
- **fix/***: Bug fix branches
- **hotfix/***: Critical production fixes
- **claude/***: AI-assisted development branches (auto-generated)

### Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Test additions or modifications
- **chore**: Build process or auxiliary tool changes

Examples:
```
feat(agent): add LLM-based alert classification
fix(slack): resolve message formatting issue
docs(readme): update installation instructions
```

### Code Review Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Ensure CI passes (linting, tests, type checking)
4. Create pull request with detailed description
5. Address review comments
6. Merge after approval

---

## Key Conventions

### Python Standards

1. **Type Hints**: Always use type hints (Python 3.10+ syntax)
   ```python
   # Good
   def process_alert(alert: Alert, context: dict[str, Any]) -> IncidentResponse:
       """Process an alert and return response"""
       pass

   # Bad - no type hints
   def process_alert(alert, context):
       pass
   ```

2. **Pydantic for Validation**: Use Pydantic schemas for data validation
   ```python
   from pydantic import BaseModel, Field, field_validator

   class AlertSchema(BaseModel):
       id: str
       severity: Literal["critical", "high", "medium", "low"]
       timestamp: datetime
       source: str

       @field_validator("severity")
       @classmethod
       def validate_severity(cls, v: str) -> str:
           if v not in ["critical", "high", "medium", "low"]:
               raise ValueError("Invalid severity")
           return v
   ```

3. **Async/Await**: Use async for I/O operations
   ```python
   # Good - async for I/O
   async def fetch_incident(incident_id: str) -> Incident:
       async with get_session() as session:
           result = await session.execute(
               select(Incident).where(Incident.id == incident_id)
           )
           return result.scalar_one()

   # Bad - blocking I/O
   def fetch_incident(incident_id: str) -> Incident:
       session = get_session()
       return session.query(Incident).filter(Incident.id == incident_id).one()
   ```

### Error Handling

1. **Use Custom Exception Classes**:
   ```python
   class IncidentError(Exception):
       """Base exception for incident-related errors"""

       def __init__(
           self,
           message: str,
           code: str,
           context: dict[str, Any] | None = None
       ):
           self.message = message
           self.code = code
           self.context = context or {}
           super().__init__(self.message)

   class AlertProcessingError(IncidentError):
       """Alert processing failed"""
       pass
   ```

2. **Async Error Handling**:
   ```python
   from app.core.logging import logger

   async def process_alert(alert: Alert) -> ProcessResult:
       try:
           result = await risky_operation(alert)
           return ProcessResult(success=True, data=result)
       except Exception as e:
           logger.error(
               "Alert processing failed",
               extra={
                   "alert_id": alert.id,
                   "error": str(e),
                   "error_type": type(e).__name__
               }
           )
           raise AlertProcessingError(
               "Failed to process alert",
               "ALERT_PROCESS_ERROR",
               {"alert_id": alert.id}
           ) from e
   ```

3. **Never Swallow Errors**: Always log or re-raise
   ```python
   # Bad
   try:
       await operation()
   except Exception:
       pass  # Silent failure

   # Good
   try:
       await operation()
   except Exception as e:
       logger.error("Operation failed", extra={"error": str(e)})
       raise
   ```

### Logging

Use structured logging with context:

```python
from app.core.logging import logger

# Include context in all logs
logger.info(
    "Processing alert",
    extra={
        "alert_id": alert.id,
        "severity": alert.severity,
        "source": alert.source,
        "correlation_id": context.correlation_id
    }
)

# Log levels:
# - error: Errors that require attention
# - warning: Warning conditions
# - info: Informational messages
# - debug: Debug information (development only)
```

### Configuration Management

Use Pydantic Settings for configuration:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Database
    database_url: str
    database_pool_size: int = 10

    # Redis
    redis_url: str

    # API Keys (never commit these!)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    pagerduty_api_key: str | None = None
    slack_bot_token: str | None = None

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    max_concurrent_incidents: int = 10

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
```

### Database Conventions

1. **Migrations**: Always use Alembic for schema changes
   ```bash
   # Create new migration
   alembic revision --autogenerate -m "add incident severity index"

   # Apply migrations
   alembic upgrade head

   # Rollback
   alembic downgrade -1
   ```

2. **SQLAlchemy Models**: Use modern SQLAlchemy 2.0 syntax
   ```python
   from sqlalchemy import String, DateTime, Enum
   from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
   from datetime import datetime

   class Base(DeclarativeBase):
       pass

   class Incident(Base):
       __tablename__ = "incidents"

       id: Mapped[str] = mapped_column(String(36), primary_key=True)
       severity: Mapped[str] = mapped_column(String(20), index=True)
       created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
       updated_at: Mapped[datetime] = mapped_column(
           DateTime,
           default=datetime.utcnow,
           onupdate=datetime.utcnow
       )
       deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
   ```

3. **Transactions**: Use async context managers
   ```python
   from app.database.session import get_session

   async def create_incident_with_alerts(incident: Incident, alerts: list[Alert]):
       async with get_session() as session:
           async with session.begin():
               session.add(incident)
               for alert in alerts:
                   alert.incident_id = incident.id
                   session.add(alert)
               await session.commit()
   ```

### API Design

1. **FastAPI Router Organization**:
   ```python
   from fastapi import APIRouter, Depends, HTTPException, status
   from app.schemas.incident import IncidentCreate, IncidentResponse
   from app.services.incident import IncidentService

   router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])

   @router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
   async def create_incident(
       incident: IncidentCreate,
       service: IncidentService = Depends(get_incident_service)
   ) -> IncidentResponse:
       """Create a new incident"""
       return await service.create(incident)
   ```

2. **Response Format**:
   ```python
   from pydantic import BaseModel

   class SuccessResponse(BaseModel):
       success: bool = True
       data: dict | list
       meta: dict | None = None

   class ErrorResponse(BaseModel):
       success: bool = False
       error: dict

       class ErrorDetail(BaseModel):
           code: str
           message: str
           details: dict | None = None
   ```

3. **Status Codes**:
   - 200: Success
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found
   - 422: Validation Error (FastAPI default)
   - 500: Internal Server Error

---

## Testing Strategy

### Test Pyramid

1. **Unit Tests** (70%): Test individual functions and classes
2. **Integration Tests** (20%): Test component interactions
3. **E2E Tests** (10%): Test complete workflows

### Testing Tools

- **Framework**: pytest
- **Async Testing**: pytest-asyncio
- **Mocking**: unittest.mock, pytest-mock
- **API Testing**: httpx (async), TestClient (FastAPI)
- **Coverage**: pytest-cov
- **Fixtures**: pytest fixtures for dependency injection

### Test Structure

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.services.alert import AlertService
from tests.factories import AlertFactory

@pytest.mark.asyncio
async def test_process_critical_alert():
    """Test that critical alerts create incidents"""
    # Arrange
    alert = AlertFactory.create(severity="critical")
    service = AlertService()

    # Act
    result = await service.process_alert(alert)

    # Assert
    assert result.incident_created is True
    assert result.incident.severity == "critical"

@pytest.mark.asyncio
async def test_alert_endpoint():
    """Test alert webhook endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhooks/alerts",
            json={"severity": "high", "message": "Test alert"}
        )

    assert response.status_code == 201
    assert response.json()["success"] is True
```

### Coverage Requirements

- **Minimum**: 80% code coverage
- **Critical Paths**: 100% coverage for core agent logic
- **Run Coverage**: `pytest --cov=app --cov-report=html`

### Testing Best Practices

1. **Use Factories**: Create test data with factories (factory_boy)
2. **Mock External APIs**: Don't call real services in tests
3. **Async Tests**: Use `@pytest.mark.asyncio` for async functions
4. **Database Isolation**: Use test database or rollback transactions
5. **Clear Naming**: Test names should describe what they test

---

## Deployment & Operations

### Environments

1. **Development**: Local development environment
2. **Staging**: Pre-production testing
3. **Production**: Live environment

### Deployment Process

```bash
# Build Docker image
docker build -t oncall-agent:latest .

# Run migrations
docker run oncall-agent:latest alembic upgrade head

# Start application
docker run -p 8000:8000 oncall-agent:latest

# Or use docker-compose
docker-compose up -d
```

### Health Checks

FastAPI endpoints for monitoring:
```python
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness_check():
    """Readiness probe - checks dependencies"""
    # Check database connection
    # Check Redis connection
    return {"status": "ready", "checks": {...}}
```

### Monitoring

1. **Metrics**: Prometheus metrics via `prometheus-fastapi-instrumentator`
2. **Logging**: Structured JSON logs to stdout
3. **Tracing**: OpenTelemetry for distributed tracing
4. **Alerts**: Alert on error rates, latency, queue depths

### Environment Variables

Required environment variables:
```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/oncall
REDIS_URL=redis://localhost:6379/0

# AI/LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Integrations
PAGERDUTY_API_KEY=...
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
JIRA_URL=https://company.atlassian.net
JIRA_API_TOKEN=...
```

---

## AI Assistant Guidelines

### When Working on This Codebase

#### 1. Understanding Context

Before making changes:
- Read relevant code sections thoroughly
- Understand the data flow and dependencies
- Check for existing patterns and conventions
- Review related tests
- Check Pydantic schemas for data validation

#### 2. Making Changes

**Always:**
- Use type hints for all functions and methods
- Write or update tests for your changes
- Update documentation if behavior changes
- Use Pydantic for request/response validation
- Add appropriate error handling
- Include structured logging for important operations
- Use async/await for I/O operations
- Follow PEP 8 style guide (use `black` formatter)

**Never:**
- Commit secrets or credentials
- Break existing tests without fixing them
- Make breaking API changes without discussion
- Skip error handling
- Use `print()` for logging (use structured logger)
- Use blocking I/O in async functions
- Ignore type hints

#### 3. Code Quality Checklist

Before committing:
- [ ] Code has proper type hints
- [ ] All tests pass (`pytest`)
- [ ] Code is formatted with `black`
- [ ] Linting passes (`ruff` or `flake8`)
- [ ] Type checking passes (`mypy`)
- [ ] No security vulnerabilities introduced
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate and structured
- [ ] Documentation/docstrings updated

#### 4. Common Tasks

**Adding a New Integration:**
1. Create module in `app/integrations/<service>/`
2. Implement the `Integration` protocol
3. Add configuration in `app/core/config.py`
4. Add Pydantic schemas for validation
5. Write integration tests with mocked API calls
6. Update documentation

**Adding a New API Endpoint:**
1. Define route in `app/api/routes/`
2. Create Pydantic schemas in `app/schemas/`
3. Implement service logic in `app/services/`
4. Add dependencies for auth/validation
5. Write tests for all scenarios (success, validation, errors)
6. Document in OpenAPI (FastAPI does this automatically)

**Modifying Database Schema:**
1. Update SQLAlchemy model in `app/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration file
4. Test migration: `alembic upgrade head` and `alembic downgrade -1`
5. Update Pydantic schemas if needed
6. Update affected tests

**Working with LLMs/Agents:**
1. Define prompts in `app/agent/prompts/`
2. Use LangChain for agent orchestration
3. Implement tools in `app/agent/tools.py`
4. Add proper error handling for LLM API calls
5. Log LLM interactions for debugging
6. Consider rate limits and costs
7. Test with mock LLM responses

#### 5. Security Considerations

Always consider:
- **Input Validation**: Use Pydantic schemas for all inputs
- **SQL Injection**: SQLAlchemy ORM prevents this, but be careful with raw queries
- **Authentication**: Use FastAPI dependencies for auth
- **Rate Limiting**: Use `slowapi` or similar
- **Secrets Management**: Never hardcode secrets, use environment variables
- **Dependency Security**: Run `pip audit` or `safety check`
- **LLM Security**: Validate and sanitize LLM inputs/outputs

#### 6. Performance Considerations

- **Database**: Use indexes, select only needed columns, avoid N+1 queries
- **Caching**: Use Redis for frequently accessed data
- **Async**: Use async/await for all I/O operations
- **Connection Pools**: Configure appropriate pool sizes
- **LLM Calls**: Cache results when possible, use streaming for long responses
- **Background Tasks**: Use Celery for long-running tasks

#### 7. Debugging Tips

When investigating issues:
1. Check structured logs with correlation IDs
2. Use FastAPI's automatic OpenAPI docs (`/docs`)
3. Test endpoints with the interactive docs
4. Use `ipdb` or VS Code debugger for breakpoints
5. Check Prometheus metrics for performance issues
6. Verify environment variables and configuration
7. Test integrations individually with unit tests

#### 8. Common Patterns

**Retry Logic with Tenacity:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_external_api() -> dict:
    """Call external API with retry logic"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        response.raise_for_status()
        return response.json()
```

**Dependency Injection (FastAPI):**
```python
from fastapi import Depends
from app.database.session import get_session

async def get_incident_service(
    session = Depends(get_session)
) -> IncidentService:
    """Dependency for incident service"""
    return IncidentService(session)

@router.get("/incidents/{incident_id}")
async def get_incident(
    incident_id: str,
    service: IncidentService = Depends(get_incident_service)
):
    return await service.get(incident_id)
```

**Background Tasks with Celery:**
```python
from celery import Celery

celery = Celery("oncall-agent", broker="redis://localhost:6379/0")

@celery.task
def process_alert_async(alert_id: str):
    """Process alert in background"""
    # Long-running task
    pass

# Trigger from API
@router.post("/alerts")
async def create_alert(alert: AlertCreate):
    # Save alert
    saved_alert = await service.create(alert)
    # Process asynchronously
    process_alert_async.delay(saved_alert.id)
    return saved_alert
```

**Caching with Redis:**
```python
from redis import asyncio as aioredis
import json

async def get_cached_incident(incident_id: str) -> Incident | None:
    """Get incident from cache"""
    redis = await aioredis.from_url("redis://localhost")
    cached = await redis.get(f"incident:{incident_id}")
    if cached:
        return Incident(**json.loads(cached))
    return None

async def cache_incident(incident: Incident, ttl: int = 300):
    """Cache incident for 5 minutes"""
    redis = await aioredis.from_url("redis://localhost")
    await redis.setex(
        f"incident:{incident.id}",
        ttl,
        json.dumps(incident.dict())
    )
```

#### 9. Integration-Specific Guidelines

**Slack Integration:**
- Use `slack-sdk` (async version)
- Verify request signatures for security
- Use Block Kit for rich messages
- Handle rate limits (1 message/second per channel)
- Use threads for related messages
- Implement slash commands for user interaction

**PagerDuty Integration:**
- Use `pdpyras` library
- Deduplicate incidents using `dedup_key`
- Map severity levels correctly
- Include relevant context in incident body
- Handle webhook verification
- Implement proper retry logic

**LLM/AI Integration:**
- Use LangChain for agent orchestration
- Implement proper error handling for API failures
- Log all LLM interactions for debugging
- Cache expensive LLM calls when possible
- Use streaming for long responses
- Monitor token usage and costs
- Validate and sanitize prompts

#### 10. Escalation Patterns

When you encounter:
- **Unclear Requirements**: Ask for clarification before implementing
- **Breaking Changes**: Discuss with team first, create migration path
- **Security Concerns**: Flag immediately and don't proceed
- **Performance Issues**: Profile first (`py-spy`, `cProfile`), then optimize
- **Complex Decisions**: Document trade-offs and rationale in comments

#### 11. Python-Specific Best Practices

**Use Modern Python Features:**
```python
# Good - Python 3.10+ type hints
def process_data(items: list[dict[str, Any]]) -> dict[str, int]:
    pass

# Good - Pattern matching (Python 3.10+)
match alert.severity:
    case "critical":
        return Priority.HIGH
    case "high" | "medium":
        return Priority.MEDIUM
    case _:
        return Priority.LOW

# Good - Walrus operator
if (incident := await fetch_incident(alert.incident_id)) is not None:
    await process_incident(incident)
```

**Context Managers:**
```python
# Always use context managers for resources
async with httpx.AsyncClient() as client:
    response = await client.get(url)

async with get_session() as session:
    await session.execute(query)
```

**List/Dict Comprehensions:**
```python
# Prefer comprehensions for transformations
active_incidents = [i for i in incidents if not i.resolved]
severity_map = {i.id: i.severity for i in incidents}
```

---

## Additional Resources

### Documentation
- `docs/architecture.md`: Detailed architecture overview
- `docs/api.md`: Complete API reference (auto-generated by FastAPI)
- `docs/runbooks/`: Operational runbooks

### External References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [LangChain Documentation](https://python.langchain.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Development Tools
- **Formatter**: `black` (run with `black app tests`)
- **Linter**: `ruff` or `flake8`
- **Type Checker**: `mypy` (run with `mypy app`)
- **Import Sorter**: `isort`
- **Security**: `bandit`, `safety`

---

## Changelog

### Version History

**v2.0.0 - 2025-11-14**
- Migrated from TypeScript to Python/FastAPI stack
- Added AI/LLM integration guidelines
- Updated all code examples to Python
- Added async/await patterns
- Included Pydantic and SQLAlchemy best practices

**v1.0.0 - 2025-11-14**
- Initial CLAUDE.md creation
- Established project structure and conventions
- Defined AI assistant guidelines

---

## Contributing

When contributing to this project:

1. Read this entire document
2. Set up your development environment (Python 3.11+, virtual environment)
3. Install pre-commit hooks: `pre-commit install`
4. Create a feature branch
5. Follow all conventions and guidelines
6. Write comprehensive tests (aim for >80% coverage)
7. Run formatters and linters before committing
8. Submit a pull request with clear description

Remember: Quality over speed. Well-tested, maintainable code is always preferred over quick but fragile solutions.

---

**Last Updated**: 2025-11-14
**Maintainers**: OnCall Agent Team
**Version**: 2.0.0
