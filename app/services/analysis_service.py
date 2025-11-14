"""Log analysis service - orchestrates log fetching, analysis, and reporting."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.exceptions import LogAnalysisError
from app.core.logging import logger
from app.integrations.gcp import GCPLoggingClient
from app.schemas.analysis import (
    LogAnalysisRequest,
    LogAnalysisResponse,
    LogStatistics,
    AnalysisFinding
)
from app.services.llm_service import LLMService
from app.services.document_service import DocumentService


class AnalysisService:
    """Service for orchestrating log analysis workflow."""

    def __init__(self):
        """Initialize the analysis service."""
        self.settings = get_settings()
        self.gcp_client = GCPLoggingClient()
        self.llm_service = LLMService()
        self.document_service = DocumentService()

        # Ensure output directory exists
        Path(self.settings.analysis_output_dir).mkdir(parents=True, exist_ok=True)

    async def analyze_logs(
        self,
        request: LogAnalysisRequest
    ) -> LogAnalysisResponse:
        """Perform complete log analysis workflow.

        Args:
            request: Log analysis request parameters

        Returns:
            Complete analysis response with findings and document path

        Raises:
            LogAnalysisError: If analysis fails at any step
        """
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        try:
            logger.info(
                "Starting log analysis",
                extra={
                    "analysis_id": analysis_id,
                    "hours_back": request.hours_back,
                    "focus_on_errors": request.focus_on_errors
                }
            )

            # Step 1: Fetch logs from GCP
            logs = self._fetch_logs(request)

            if not logs:
                logger.warning("No logs found for analysis")
                return self._create_empty_response(analysis_id, timestamp, request)

            # Step 2: Get log statistics
            statistics = self._calculate_statistics(logs, request.hours_back)

            # Step 3: Analyze logs with LLM
            llm_analysis = self.llm_service.analyze_logs(logs, statistics)

            # Step 4: Convert to response format
            findings = self._convert_findings(llm_analysis.get("findings", []))

            # Step 5: Generate document
            document_path = self.document_service.generate_document(
                analysis_id=analysis_id,
                timestamp=timestamp,
                statistics=statistics,
                findings=findings,
                summary=llm_analysis.get("summary", ""),
                recommendations=llm_analysis.get("recommendations", []),
                output_format=request.output_format
            )

            # Step 6: Create response
            response = LogAnalysisResponse(
                analysis_id=analysis_id,
                timestamp=timestamp,
                statistics=LogStatistics(
                    total_logs=statistics["total_count"],
                    by_severity=statistics["by_severity"],
                    time_range_hours=statistics["time_range_hours"],
                    most_common_errors=llm_analysis.get("most_common_errors", [])
                ),
                findings=findings,
                summary=llm_analysis.get("summary", ""),
                document_path=document_path,
                recommendations=llm_analysis.get("recommendations", [])
            )

            logger.info(
                "Log analysis completed successfully",
                extra={
                    "analysis_id": analysis_id,
                    "findings_count": len(findings),
                    "document_path": document_path
                }
            )

            return response

        except Exception as e:
            logger.error(
                "Log analysis failed",
                extra={
                    "analysis_id": analysis_id,
                    "error": str(e)
                }
            )
            raise LogAnalysisError(
                f"Log analysis failed: {str(e)}",
                "ANALYSIS_ERROR",
                {"analysis_id": analysis_id, "error": str(e)}
            ) from e

    def _fetch_logs(self, request: LogAnalysisRequest) -> list[dict[str, Any]]:
        """Fetch logs based on request parameters.

        Args:
            request: Log analysis request

        Returns:
            List of log entries
        """
        if request.focus_on_errors:
            return self.gcp_client.fetch_error_logs(
                hours_back=request.hours_back,
                max_results=request.max_logs
            )
        else:
            return self.gcp_client.fetch_logs(
                filter_query=request.filter_query,
                hours_back=request.hours_back,
                max_results=request.max_logs
            )

    def _calculate_statistics(
        self,
        logs: list[dict[str, Any]],
        hours_back: int
    ) -> dict[str, Any]:
        """Calculate statistics from logs.

        Args:
            logs: List of log entries
            hours_back: Time range in hours

        Returns:
            Statistics dictionary
        """
        stats = {
            "total_count": len(logs),
            "by_severity": {},
            "time_range_hours": hours_back
        }

        for log in logs:
            severity = log.get("severity", "UNKNOWN")
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1

        return stats

    def _convert_findings(
        self,
        llm_findings: list[dict[str, Any]]
    ) -> list[AnalysisFinding]:
        """Convert LLM findings to schema objects.

        Args:
            llm_findings: Raw findings from LLM

        Returns:
            List of AnalysisFinding objects
        """
        findings = []
        for finding in llm_findings:
            try:
                findings.append(AnalysisFinding(
                    severity=finding.get("severity", "info"),
                    title=finding.get("title", "Unknown issue"),
                    description=finding.get("description", ""),
                    affected_logs_count=finding.get("affected_logs_count", 0),
                    suggested_fix=finding.get("suggested_fix", ""),
                    code_example=finding.get("code_example")
                ))
            except Exception as e:
                logger.warning(
                    "Failed to convert finding",
                    extra={"error": str(e), "finding": finding}
                )
                continue

        return findings

    def _create_empty_response(
        self,
        analysis_id: str,
        timestamp: datetime,
        request: LogAnalysisRequest
    ) -> LogAnalysisResponse:
        """Create an empty response when no logs are found.

        Args:
            analysis_id: Analysis ID
            timestamp: Analysis timestamp
            request: Original request

        Returns:
            Empty analysis response
        """
        return LogAnalysisResponse(
            analysis_id=analysis_id,
            timestamp=timestamp,
            statistics=LogStatistics(
                total_logs=0,
                by_severity={},
                time_range_hours=request.hours_back,
                most_common_errors=[]
            ),
            findings=[],
            summary="No logs found in the specified time range.",
            document_path=None,
            recommendations=["Check your GCP logging configuration and filters."]
        )

    def get_analysis_status(self, analysis_id: str) -> dict[str, Any]:
        """Get the status of an analysis (for future async implementation).

        Args:
            analysis_id: Analysis ID to check

        Returns:
            Status information
        """
        # Placeholder for future async job tracking
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "message": "Analysis completed"
        }
