"""GCP Cloud Logging integration client."""

import json
from datetime import datetime, timedelta
from typing import Any

from google.cloud import logging
from google.oauth2 import service_account

from app.core.config import get_settings
from app.core.exceptions import GCPIntegrationError
from app.core.logging import logger


class GCPLoggingClient:
    """Client for fetching logs from GCP Cloud Logging."""

    def __init__(self):
        """Initialize the GCP Logging client."""
        self.settings = get_settings()
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the GCP logging client with credentials."""
        try:
            if not self.settings.gcp_project_id:
                raise GCPIntegrationError(
                    "GCP project ID not configured",
                    "GCP_PROJECT_ID_MISSING"
                )

            # Initialize with credentials if provided
            if self.settings.gcp_credentials_json:
                try:
                    # Try to load as JSON file path first
                    credentials = service_account.Credentials.from_service_account_file(
                        self.settings.gcp_credentials_json
                    )
                except FileNotFoundError:
                    # If not a file, try to parse as JSON string
                    credentials_dict = json.loads(self.settings.gcp_credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_dict
                    )

                self.client = logging.Client(
                    project=self.settings.gcp_project_id,
                    credentials=credentials
                )
            else:
                # Use default credentials (e.g., from GCE metadata server)
                self.client = logging.Client(
                    project=self.settings.gcp_project_id
                )

            logger.info(
                "GCP Logging client initialized",
                extra={"project_id": self.settings.gcp_project_id}
            )

        except Exception as e:
            logger.error(
                "Failed to initialize GCP Logging client",
                extra={"error": str(e)}
            )
            raise GCPIntegrationError(
                f"Failed to initialize GCP Logging client: {str(e)}",
                "GCP_CLIENT_INIT_ERROR",
                {"error": str(e)}
            ) from e

    def fetch_logs(
        self,
        filter_query: str | None = None,
        hours_back: int = 24,
        max_results: int | None = None
    ) -> list[dict[str, Any]]:
        """Fetch logs from GCP Cloud Logging.

        Args:
            filter_query: Cloud Logging filter query (optional)
            hours_back: Number of hours to look back (default: 24)
            max_results: Maximum number of log entries to return (default: from settings)

        Returns:
            List of log entries as dictionaries

        Raises:
            GCPIntegrationError: If log fetching fails
        """
        if not self.client:
            raise GCPIntegrationError(
                "GCP Logging client not initialized",
                "GCP_CLIENT_NOT_INITIALIZED"
            )

        try:
            # Build the filter
            timestamp_filter = self._build_timestamp_filter(hours_back)

            # Combine with user-provided filter
            if filter_query:
                full_filter = f"{timestamp_filter} AND {filter_query}"
            elif self.settings.gcp_log_filter:
                full_filter = f"{timestamp_filter} AND {self.settings.gcp_log_filter}"
            else:
                full_filter = timestamp_filter

            logger.info(
                "Fetching logs from GCP",
                extra={
                    "filter": full_filter,
                    "hours_back": hours_back,
                    "max_results": max_results or self.settings.gcp_log_limit
                }
            )

            # Fetch logs
            entries = self.client.list_entries(
                filter_=full_filter,
                page_size=max_results or self.settings.gcp_log_limit
            )

            # Convert to list of dictionaries
            log_entries = []
            for entry in entries:
                log_entry = {
                    "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                    "severity": entry.severity,
                    "log_name": entry.log_name,
                    "resource": self._format_resource(entry.resource),
                    "text_payload": entry.payload if isinstance(entry.payload, str) else None,
                    "json_payload": entry.payload if isinstance(entry.payload, dict) else None,
                    "labels": entry.labels,
                    "insert_id": entry.insert_id,
                }
                log_entries.append(log_entry)

            logger.info(
                "Successfully fetched logs from GCP",
                extra={"count": len(log_entries)}
            )

            return log_entries

        except Exception as e:
            logger.error(
                "Failed to fetch logs from GCP",
                extra={"error": str(e)}
            )
            raise GCPIntegrationError(
                f"Failed to fetch logs: {str(e)}",
                "GCP_LOG_FETCH_ERROR",
                {"error": str(e)}
            ) from e

    def fetch_error_logs(
        self,
        hours_back: int = 24,
        max_results: int | None = None
    ) -> list[dict[str, Any]]:
        """Fetch error and warning logs from GCP.

        Args:
            hours_back: Number of hours to look back (default: 24)
            max_results: Maximum number of log entries to return

        Returns:
            List of error/warning log entries
        """
        error_filter = 'severity >= "WARNING"'
        return self.fetch_logs(
            filter_query=error_filter,
            hours_back=hours_back,
            max_results=max_results
        )

    def _build_timestamp_filter(self, hours_back: int) -> str:
        """Build a timestamp filter for Cloud Logging.

        Args:
            hours_back: Number of hours to look back

        Returns:
            Timestamp filter string
        """
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        # Format: timestamp >= "2024-01-01T00:00:00Z"
        return f'timestamp >= "{start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}"'

    def _format_resource(self, resource: Any) -> dict[str, Any]:
        """Format a log resource object to a dictionary.

        Args:
            resource: GCP log resource object

        Returns:
            Dictionary representation of the resource
        """
        if not resource:
            return {}

        return {
            "type": resource.type if hasattr(resource, "type") else None,
            "labels": dict(resource.labels) if hasattr(resource, "labels") else {}
        }

    def get_log_statistics(
        self,
        hours_back: int = 24
    ) -> dict[str, Any]:
        """Get statistics about logs (count by severity).

        Args:
            hours_back: Number of hours to look back

        Returns:
            Dictionary with log statistics
        """
        try:
            logs = self.fetch_logs(hours_back=hours_back)

            stats = {
                "total_count": len(logs),
                "by_severity": {},
                "time_range_hours": hours_back
            }

            # Count by severity
            for log in logs:
                severity = log.get("severity", "UNKNOWN")
                stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1

            return stats

        except Exception as e:
            logger.error(
                "Failed to get log statistics",
                extra={"error": str(e)}
            )
            raise GCPIntegrationError(
                f"Failed to get log statistics: {str(e)}",
                "GCP_STATS_ERROR",
                {"error": str(e)}
            ) from e
