"""Custom exception classes."""

from typing import Any


class OnCallAgentError(Exception):
    """Base exception for OnCall Agent errors."""

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


class GCPIntegrationError(OnCallAgentError):
    """GCP integration related errors."""
    pass


class LogAnalysisError(OnCallAgentError):
    """Log analysis related errors."""
    pass


class LLMError(OnCallAgentError):
    """LLM API related errors."""
    pass
