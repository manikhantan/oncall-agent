"""LLM service for AI-powered analysis."""

import json
from typing import Any

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.core.logging import logger


class LLMService:
    """Service for interacting with LLM providers (OpenAI, Anthropic)."""

    def __init__(self):
        """Initialize the LLM service."""
        self.settings = get_settings()
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration."""
        try:
            if self.settings.llm_provider == "anthropic":
                if not self.settings.anthropic_api_key:
                    raise LLMError(
                        "Anthropic API key not configured",
                        "ANTHROPIC_API_KEY_MISSING"
                    )
                logger.info("Initializing Anthropic LLM")
                return ChatAnthropic(
                    model=self.settings.llm_model or "claude-3-sonnet-20240229",
                    anthropic_api_key=self.settings.anthropic_api_key,
                    temperature=self.settings.llm_temperature
                )
            else:  # default to OpenAI
                if not self.settings.openai_api_key:
                    raise LLMError(
                        "OpenAI API key not configured",
                        "OPENAI_API_KEY_MISSING"
                    )
                logger.info("Initializing OpenAI LLM")
                return ChatOpenAI(
                    model=self.settings.llm_model or "gpt-4",
                    openai_api_key=self.settings.openai_api_key,
                    temperature=self.settings.llm_temperature
                )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise LLMError(
                f"Failed to initialize LLM: {str(e)}",
                "LLM_INIT_ERROR",
                {"error": str(e)}
            ) from e

    def analyze_logs(
        self,
        logs: list[dict[str, Any]],
        statistics: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze logs using LLM and generate findings.

        Args:
            logs: List of log entries to analyze
            statistics: Statistics about the logs

        Returns:
            Dictionary containing analysis results with findings and recommendations

        Raises:
            LLMError: If LLM analysis fails
        """
        try:
            logger.info(
                "Starting LLM log analysis",
                extra={"log_count": len(logs)}
            )

            # Prepare log data for analysis
            log_summary = self._prepare_log_summary(logs)

            # Create the analysis prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                ("human", self._get_analysis_prompt(log_summary, statistics))
            ])

            # Get LLM response
            chain = prompt | self.llm
            response = chain.invoke({})

            # Parse the response
            analysis_result = self._parse_llm_response(response.content)

            logger.info("LLM analysis completed successfully")
            return analysis_result

        except Exception as e:
            logger.error(
                "LLM analysis failed",
                extra={"error": str(e)}
            )
            raise LLMError(
                f"Failed to analyze logs with LLM: {str(e)}",
                "LLM_ANALYSIS_ERROR",
                {"error": str(e)}
            ) from e

    def _prepare_log_summary(self, logs: list[dict[str, Any]]) -> str:
        """Prepare a summary of logs for LLM analysis.

        Args:
            logs: List of log entries

        Returns:
            Formatted string summary of logs
        """
        # Limit number of logs to analyze
        max_logs = self.settings.max_log_entries_to_analyze
        logs_to_analyze = logs[:max_logs]

        summary_parts = []
        for i, log in enumerate(logs_to_analyze, 1):
            log_text = f"Log #{i}:\n"
            log_text += f"  Timestamp: {log.get('timestamp', 'N/A')}\n"
            log_text += f"  Severity: {log.get('severity', 'N/A')}\n"
            log_text += f"  Log Name: {log.get('log_name', 'N/A')}\n"

            # Include payload
            if log.get('text_payload'):
                log_text += f"  Message: {log['text_payload']}\n"
            elif log.get('json_payload'):
                log_text += f"  JSON: {json.dumps(log['json_payload'], indent=2)}\n"

            # Include resource info
            if log.get('resource'):
                log_text += f"  Resource Type: {log['resource'].get('type', 'N/A')}\n"

            summary_parts.append(log_text)

        return "\n".join(summary_parts)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for log analysis."""
        return """You are an expert system reliability engineer and log analyst.
Your task is to analyze GCP Cloud Logging entries and identify issues, errors, and patterns.

Provide your analysis in the following JSON format:
{
  "summary": "Brief executive summary of the overall log analysis",
  "findings": [
    {
      "severity": "critical|high|medium|low|info",
      "title": "Short title of the finding",
      "description": "Detailed description of the issue",
      "affected_logs_count": number,
      "suggested_fix": "Concrete steps to fix or mitigate the issue",
      "code_example": "Code example if applicable (optional)"
    }
  ],
  "recommendations": [
    "General recommendation 1",
    "General recommendation 2"
  ],
  "most_common_errors": [
    "Error pattern 1",
    "Error pattern 2"
  ]
}

Focus on:
1. Identifying error patterns and root causes
2. Suggesting concrete, actionable fixes
3. Prioritizing findings by severity and impact
4. Providing code examples when relevant
5. Explaining the business/operational impact"""

    def _get_analysis_prompt(
        self,
        log_summary: str,
        statistics: dict[str, Any]
    ) -> str:
        """Get the analysis prompt with log data.

        Args:
            log_summary: Formatted summary of logs
            statistics: Statistics about the logs

        Returns:
            Formatted prompt string
        """
        return f"""Please analyze the following GCP logs and provide findings and recommendations.

Statistics:
- Total logs analyzed: {statistics.get('total_count', 0)}
- Time range: {statistics.get('time_range_hours', 0)} hours
- Severity breakdown: {json.dumps(statistics.get('by_severity', {}), indent=2)}

Logs:
{log_summary}

Provide your analysis in the specified JSON format."""

    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        """Parse LLM response into structured format.

        Args:
            response: Raw LLM response text

        Returns:
            Parsed analysis results

        Raises:
            LLMError: If parsing fails
        """
        try:
            # Try to extract JSON from the response
            # LLMs sometimes wrap JSON in markdown code blocks
            response = response.strip()

            if response.startswith("```json"):
                response = response[7:]  # Remove ```json
            if response.startswith("```"):
                response = response[3:]  # Remove ```
            if response.endswith("```"):
                response = response[:-3]  # Remove trailing ```

            response = response.strip()

            # Parse JSON
            result = json.loads(response)

            # Validate required fields
            if "summary" not in result:
                result["summary"] = "Analysis completed"
            if "findings" not in result:
                result["findings"] = []
            if "recommendations" not in result:
                result["recommendations"] = []
            if "most_common_errors" not in result:
                result["most_common_errors"] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse LLM response as JSON",
                extra={"error": str(e), "response": response[:500]}
            )
            # Return a basic structure if parsing fails
            return {
                "summary": "Analysis completed but response parsing failed",
                "findings": [{
                    "severity": "info",
                    "title": "Analysis Result",
                    "description": response[:1000],
                    "affected_logs_count": 0,
                    "suggested_fix": "Manual review required"
                }],
                "recommendations": ["Review logs manually"],
                "most_common_errors": []
            }
