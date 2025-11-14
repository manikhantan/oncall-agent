"""Unit tests for GCP integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.integrations.gcp.logging_client import GCPLoggingClient
from app.core.exceptions import GCPIntegrationError


class TestGCPLoggingClient:
    """Tests for GCP Logging Client."""

    @patch("app.integrations.gcp.logging_client.logging.Client")
    @patch("app.integrations.gcp.logging_client.get_settings")
    def test_initialization_success(self, mock_settings, mock_logging_client):
        """Test successful client initialization."""
        # Arrange
        mock_settings.return_value.gcp_project_id = "test-project"
        mock_settings.return_value.gcp_credentials_json = None

        # Act
        client = GCPLoggingClient()

        # Assert
        assert client.client is not None
        mock_logging_client.assert_called_once()

    @patch("app.integrations.gcp.logging_client.get_settings")
    def test_initialization_fails_without_project_id(self, mock_settings):
        """Test that initialization fails without project ID."""
        # Arrange
        mock_settings.return_value.gcp_project_id = None

        # Act & Assert
        with pytest.raises(GCPIntegrationError) as exc_info:
            GCPLoggingClient()

        assert exc_info.value.code == "GCP_PROJECT_ID_MISSING"

    @patch("app.integrations.gcp.logging_client.logging.Client")
    @patch("app.integrations.gcp.logging_client.get_settings")
    def test_fetch_logs_success(self, mock_settings, mock_logging_client, mock_gcp_logs):
        """Test successful log fetching."""
        # Arrange
        mock_settings.return_value.gcp_project_id = "test-project"
        mock_settings.return_value.gcp_credentials_json = None
        mock_settings.return_value.gcp_log_filter = ""
        mock_settings.return_value.gcp_log_limit = 100

        mock_client_instance = MagicMock()
        mock_logging_client.return_value = mock_client_instance

        # Create mock log entries
        mock_entries = []
        for log in mock_gcp_logs:
            mock_entry = MagicMock()
            mock_entry.timestamp = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            mock_entry.severity = log["severity"]
            mock_entry.log_name = log["log_name"]
            mock_entry.payload = log["text_payload"]
            mock_entry.labels = log["labels"]
            mock_entry.insert_id = log["insert_id"]
            mock_entry.resource = MagicMock()
            mock_entry.resource.type = log["resource"]["type"]
            mock_entry.resource.labels = log["resource"]["labels"]
            mock_entries.append(mock_entry)

        mock_client_instance.list_entries.return_value = mock_entries

        # Act
        client = GCPLoggingClient()
        result = client.fetch_logs(hours_back=24)

        # Assert
        assert len(result) == len(mock_gcp_logs)
        assert result[0]["severity"] == "ERROR"
        assert result[1]["severity"] == "WARNING"

    @patch("app.integrations.gcp.logging_client.logging.Client")
    @patch("app.integrations.gcp.logging_client.get_settings")
    def test_fetch_error_logs(self, mock_settings, mock_logging_client, mock_gcp_logs):
        """Test fetching error logs specifically."""
        # Arrange
        mock_settings.return_value.gcp_project_id = "test-project"
        mock_settings.return_value.gcp_credentials_json = None
        mock_settings.return_value.gcp_log_filter = ""
        mock_settings.return_value.gcp_log_limit = 100

        mock_client_instance = MagicMock()
        mock_logging_client.return_value = mock_client_instance

        # Only return ERROR logs
        error_logs = [log for log in mock_gcp_logs if log["severity"] == "ERROR"]
        mock_entries = []
        for log in error_logs:
            mock_entry = MagicMock()
            mock_entry.timestamp = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            mock_entry.severity = log["severity"]
            mock_entry.log_name = log["log_name"]
            mock_entry.payload = log["text_payload"]
            mock_entry.labels = log["labels"]
            mock_entry.insert_id = log["insert_id"]
            mock_entry.resource = MagicMock()
            mock_entry.resource.type = log["resource"]["type"]
            mock_entry.resource.labels = log["resource"]["labels"]
            mock_entries.append(mock_entry)

        mock_client_instance.list_entries.return_value = mock_entries

        # Act
        client = GCPLoggingClient()
        result = client.fetch_error_logs(hours_back=24)

        # Assert
        assert len(result) == 2  # Only ERROR logs
        assert all(log["severity"] == "ERROR" for log in result)

    @patch("app.integrations.gcp.logging_client.logging.Client")
    @patch("app.integrations.gcp.logging_client.get_settings")
    def test_get_log_statistics(self, mock_settings, mock_logging_client, mock_gcp_logs):
        """Test getting log statistics."""
        # Arrange
        mock_settings.return_value.gcp_project_id = "test-project"
        mock_settings.return_value.gcp_credentials_json = None
        mock_settings.return_value.gcp_log_filter = ""
        mock_settings.return_value.gcp_log_limit = 100

        mock_client_instance = MagicMock()
        mock_logging_client.return_value = mock_client_instance

        mock_entries = []
        for log in mock_gcp_logs:
            mock_entry = MagicMock()
            mock_entry.timestamp = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            mock_entry.severity = log["severity"]
            mock_entry.log_name = log["log_name"]
            mock_entry.payload = log["text_payload"]
            mock_entry.labels = log["labels"]
            mock_entry.insert_id = log["insert_id"]
            mock_entry.resource = MagicMock()
            mock_entry.resource.type = log["resource"]["type"]
            mock_entry.resource.labels = log["resource"]["labels"]
            mock_entries.append(mock_entry)

        mock_client_instance.list_entries.return_value = mock_entries

        # Act
        client = GCPLoggingClient()
        stats = client.get_log_statistics(hours_back=24)

        # Assert
        assert stats["total_count"] == 3
        assert stats["by_severity"]["ERROR"] == 2
        assert stats["by_severity"]["WARNING"] == 1
        assert stats["time_range_hours"] == 24
