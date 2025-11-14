"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging, logger
from app.api.routes import analysis


# Setup logging
setup_logging()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="OnCall Agent - GCP Log Analysis",
    description="Intelligent log analysis and automated fix suggestions for GCP logs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(
        "Starting OnCall Agent",
        extra={
            "environment": settings.environment,
            "port": settings.port
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down OnCall Agent")


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "oncall-agent",
        "version": "0.1.0"
    }


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe - checks dependencies."""
    checks = {
        "api": "ready",
    }

    # Check if GCP is configured
    if settings.gcp_project_id:
        checks["gcp"] = "configured"
    else:
        checks["gcp"] = "not_configured"

    # Check if LLM is configured
    if settings.openai_api_key or settings.anthropic_api_key:
        checks["llm"] = "configured"
    else:
        checks["llm"] = "not_configured"

    return {
        "status": "ready",
        "checks": checks
    }


# Include routers
app.include_router(analysis.router, prefix="/api/v1")
