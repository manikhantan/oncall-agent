"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime


@pytest.fixture
def mock_gcp_logs():
    """Mock GCP log entries."""
    return [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "severity": "ERROR",
            "log_name": "projects/test-project/logs/app-error",
            "resource": {"type": "gce_instance", "labels": {}},
            "text_payload": "Database connection failed",
            "json_payload": None,
            "labels": {},
            "insert_id": "test-id-1"
        },
        {
            "timestamp": "2024-01-15T10:31:00Z",
            "severity": "WARNING",
            "log_name": "projects/test-project/logs/app-warning",
            "resource": {"type": "gce_instance", "labels": {}},
            "text_payload": "High memory usage detected",
            "json_payload": None,
            "labels": {},
            "insert_id": "test-id-2"
        },
        {
            "timestamp": "2024-01-15T10:32:00Z",
            "severity": "ERROR",
            "log_name": "projects/test-project/logs/app-error",
            "resource": {"type": "k8s_container", "labels": {}},
            "text_payload": "API timeout error",
            "json_payload": None,
            "labels": {},
            "insert_id": "test-id-3"
        }
    ]


@pytest.fixture
def mock_llm_analysis():
    """Mock LLM analysis result."""
    return {
        "summary": "Found 2 critical issues affecting database connectivity and API performance",
        "findings": [
            {
                "severity": "critical",
                "title": "Database Connection Failures",
                "description": "Multiple database connection failures detected in the logs",
                "affected_logs_count": 1,
                "suggested_fix": "Check database credentials and connection pool configuration",
                "code_example": "# Increase connection pool size\ndb_config = {'pool_size': 20, 'max_overflow': 10}"
            },
            {
                "severity": "high",
                "title": "API Timeout Errors",
                "description": "API requests are timing out, indicating performance issues",
                "affected_logs_count": 1,
                "suggested_fix": "Increase timeout values and optimize API endpoints",
                "code_example": None
            }
        ],
        "recommendations": [
            "Monitor database connection pool usage",
            "Implement circuit breaker pattern for external API calls",
            "Set up alerting for error rate thresholds"
        ],
        "most_common_errors": [
            "Database connection failed",
            "API timeout error"
        ]
    }


@pytest.fixture
def mock_log_statistics():
    """Mock log statistics."""
    return {
        "total_count": 3,
        "by_severity": {
            "ERROR": 2,
            "WARNING": 1
        },
        "time_range_hours": 24
    }
