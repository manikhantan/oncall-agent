"""Schemas for log analysis requests and responses."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class LogAnalysisRequest(BaseModel):
    """Request schema for log analysis."""

    hours_back: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Number of hours to look back (1-168 hours)"
    )
    filter_query: str | None = Field(
        default=None,
        description="Custom GCP Cloud Logging filter query"
    )
    max_logs: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Maximum number of logs to analyze (1-1000)"
    )
    focus_on_errors: bool = Field(
        default=True,
        description="Focus only on error and warning logs"
    )
    output_format: Literal["markdown", "json"] = Field(
        default="markdown",
        description="Format of the analysis output document"
    )


class LogStatistics(BaseModel):
    """Statistics about analyzed logs."""

    total_logs: int = Field(description="Total number of logs analyzed")
    by_severity: dict[str, int] = Field(description="Count of logs by severity level")
    time_range_hours: int = Field(description="Time range of logs in hours")
    most_common_errors: list[str] = Field(
        default_factory=list,
        description="Most common error patterns"
    )


class AnalysisFinding(BaseModel):
    """A single finding from log analysis."""

    severity: Literal["critical", "high", "medium", "low", "info"] = Field(
        description="Severity of the finding"
    )
    title: str = Field(description="Short title of the finding")
    description: str = Field(description="Detailed description")
    affected_logs_count: int = Field(
        default=0,
        description="Number of logs related to this finding"
    )
    suggested_fix: str = Field(description="Suggested fix or remediation")
    code_example: str | None = Field(
        default=None,
        description="Code example for the fix (if applicable)"
    )


class LogAnalysisResponse(BaseModel):
    """Response schema for log analysis."""

    analysis_id: str = Field(description="Unique identifier for this analysis")
    timestamp: datetime = Field(description="When the analysis was performed")
    statistics: LogStatistics = Field(description="Statistics about the logs")
    findings: list[AnalysisFinding] = Field(
        description="List of findings and issues discovered"
    )
    summary: str = Field(description="Executive summary of the analysis")
    document_path: str | None = Field(
        default=None,
        description="Path to the generated analysis document"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="General recommendations"
    )


class AnalysisStatusResponse(BaseModel):
    """Status response for analysis job."""

    status: Literal["pending", "running", "completed", "failed"]
    analysis_id: str
    message: str | None = None
    progress_percentage: int | None = None
