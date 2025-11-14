"""Unit tests for document service."""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

from app.services.document_service import DocumentService
from app.schemas.analysis import AnalysisFinding


class TestDocumentService:
    """Tests for Document Service."""

    @pytest.fixture
    def document_service(self):
        """Create a document service instance."""
        return DocumentService()

    @pytest.fixture
    def sample_findings(self):
        """Create sample findings."""
        return [
            AnalysisFinding(
                severity="critical",
                title="Database Connection Failures",
                description="Multiple database connection failures detected",
                affected_logs_count=5,
                suggested_fix="Check database credentials and connection pool",
                code_example="db_config = {'pool_size': 20}"
            ),
            AnalysisFinding(
                severity="high",
                title="API Timeout Errors",
                description="API requests are timing out",
                affected_logs_count=3,
                suggested_fix="Increase timeout values",
                code_example=None
            )
        ]

    @pytest.fixture
    def sample_statistics(self):
        """Create sample statistics."""
        return {
            "total_count": 10,
            "by_severity": {"ERROR": 7, "WARNING": 3},
            "time_range_hours": 24
        }

    def test_generate_markdown_document(
        self,
        document_service,
        sample_findings,
        sample_statistics,
        tmp_path
    ):
        """Test generating markdown document."""
        # Arrange
        analysis_id = "test-123"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        summary = "Test summary"
        recommendations = ["Recommendation 1", "Recommendation 2"]

        # Mock the output directory
        with patch.object(document_service.settings, "analysis_output_dir", str(tmp_path)):
            # Act
            result_path = document_service.generate_document(
                analysis_id=analysis_id,
                timestamp=timestamp,
                statistics=sample_statistics,
                findings=sample_findings,
                summary=summary,
                recommendations=recommendations,
                output_format="markdown"
            )

            # Assert
            assert Path(result_path).exists()
            with open(result_path, 'r') as f:
                content = f.read()

            # Check content
            assert "# GCP Log Analysis Report" in content
            assert analysis_id in content
            assert "Test summary" in content
            assert "Database Connection Failures" in content
            assert "API Timeout Errors" in content
            assert "Recommendation 1" in content

    def test_generate_json_document(
        self,
        document_service,
        sample_findings,
        sample_statistics,
        tmp_path
    ):
        """Test generating JSON document."""
        # Arrange
        analysis_id = "test-456"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        summary = "Test summary"
        recommendations = ["Recommendation 1"]

        # Mock the output directory
        with patch.object(document_service.settings, "analysis_output_dir", str(tmp_path)):
            # Act
            result_path = document_service.generate_document(
                analysis_id=analysis_id,
                timestamp=timestamp,
                statistics=sample_statistics,
                findings=sample_findings,
                summary=summary,
                recommendations=recommendations,
                output_format="json"
            )

            # Assert
            assert Path(result_path).exists()
            with open(result_path, 'r') as f:
                data = json.load(f)

            # Check structure
            assert data["analysis_id"] == analysis_id
            assert data["summary"] == summary
            assert len(data["findings"]) == 2
            assert data["findings"][0]["severity"] == "critical"
            assert len(data["recommendations"]) == 1

    def test_severity_emoji_mapping(self, document_service):
        """Test that severity emojis are correctly mapped."""
        assert document_service._get_severity_emoji("critical") == "🔴"
        assert document_service._get_severity_emoji("high") == "🟠"
        assert document_service._get_severity_emoji("medium") == "🟡"
        assert document_service._get_severity_emoji("low") == "🟢"
        assert document_service._get_severity_emoji("info") == "ℹ️"
        assert document_service._get_severity_emoji("unknown") == "⚪"
