"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "oncall-agent"


@pytest.mark.asyncio
async def test_readiness_check():
    """Test the readiness check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data


@pytest.mark.asyncio
@patch("app.api.routes.analysis.AnalysisService")
async def test_analyze_logs_endpoint(mock_service_class, mock_gcp_logs, mock_llm_analysis):
    """Test the log analysis endpoint."""
    # Arrange
    mock_service = AsyncMock()
    mock_service_class.return_value = mock_service

    # Mock the analysis response
    from datetime import datetime
    from app.schemas.analysis import LogAnalysisResponse, LogStatistics, AnalysisFinding

    mock_response = LogAnalysisResponse(
        analysis_id="test-123",
        timestamp=datetime.utcnow(),
        statistics=LogStatistics(
            total_logs=3,
            by_severity={"ERROR": 2, "WARNING": 1},
            time_range_hours=24,
            most_common_errors=["Database error", "API timeout"]
        ),
        findings=[
            AnalysisFinding(
                severity="critical",
                title="Test Finding",
                description="Test description",
                affected_logs_count=2,
                suggested_fix="Test fix"
            )
        ],
        summary="Test summary",
        document_path="/tmp/test_report.md",
        recommendations=["Test recommendation"]
    )

    mock_service.analyze_logs.return_value = mock_response

    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analysis/",
            json={
                "hours_back": 24,
                "focus_on_errors": True,
                "output_format": "markdown"
            }
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == "test-123"
    assert data["statistics"]["total_logs"] == 3
    assert len(data["findings"]) == 1
    assert data["findings"][0]["title"] == "Test Finding"


@pytest.mark.asyncio
async def test_analyze_logs_validation_error():
    """Test that invalid input returns validation error."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analysis/",
            json={
                "hours_back": 200,  # Exceeds max of 168
                "focus_on_errors": True
            }
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_analysis_status():
    """Test getting analysis status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analysis/status/test-123")

    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == "test-123"
    assert data["status"] == "completed"
