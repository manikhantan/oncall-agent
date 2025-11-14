"""API routes for log analysis."""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import (
    GCPIntegrationError,
    LogAnalysisError,
    LLMError
)
from app.core.logging import logger
from app.schemas.analysis import (
    LogAnalysisRequest,
    LogAnalysisResponse,
    AnalysisStatusResponse
)
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "/",
    response_model=LogAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze GCP logs",
    description="Fetch logs from GCP, analyze them with LLM, and generate a report with fix suggestions"
)
async def analyze_logs(request: LogAnalysisRequest) -> LogAnalysisResponse:
    """
    Analyze GCP logs and generate fix suggestions.

    This endpoint will:
    1. Fetch logs from GCP Cloud Logging based on the specified time range
    2. Analyze the logs using AI/LLM to identify issues and patterns
    3. Generate a detailed report with findings and suggested fixes
    4. Save the report to a file (markdown or JSON format)

    Args:
        request: Log analysis request with parameters

    Returns:
        Complete analysis response with findings and document path

    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(
            "Received log analysis request",
            extra={
                "hours_back": request.hours_back,
                "focus_on_errors": request.focus_on_errors,
                "output_format": request.output_format
            }
        )

        service = AnalysisService()
        result = await service.analyze_logs(request)

        return result

    except GCPIntegrationError as e:
        logger.error(
            "GCP integration error during analysis",
            extra={"error": str(e), "code": e.code}
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "GCP integration failed",
                "message": e.message,
                "code": e.code
            }
        )
    except LLMError as e:
        logger.error(
            "LLM error during analysis",
            extra={"error": str(e), "code": e.code}
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "LLM analysis failed",
                "message": e.message,
                "code": e.code
            }
        )
    except LogAnalysisError as e:
        logger.error(
            "Log analysis error",
            extra={"error": str(e), "code": e.code}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Analysis failed",
                "message": e.message,
                "code": e.code
            }
        )
    except Exception as e:
        logger.error(
            "Unexpected error during analysis",
            extra={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )


@router.get(
    "/status/{analysis_id}",
    response_model=AnalysisStatusResponse,
    summary="Get analysis status",
    description="Get the status of a log analysis job (for future async implementation)"
)
async def get_analysis_status(analysis_id: str) -> AnalysisStatusResponse:
    """
    Get the status of a log analysis job.

    This is a placeholder for future async job tracking functionality.

    Args:
        analysis_id: The analysis ID to check

    Returns:
        Status information for the analysis
    """
    try:
        service = AnalysisService()
        status_info = service.get_analysis_status(analysis_id)

        return AnalysisStatusResponse(
            status="completed",
            analysis_id=analysis_id,
            message="Analysis completed",
            progress_percentage=100
        )

    except Exception as e:
        logger.error(
            "Failed to get analysis status",
            extra={"error": str(e), "analysis_id": analysis_id}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Analysis not found",
                "message": str(e)
            }
        )


@router.get(
    "/quick-stats",
    summary="Get quick log statistics",
    description="Get quick statistics about logs without full analysis"
)
async def get_quick_stats(hours_back: int = 24):
    """
    Get quick statistics about logs without performing full analysis.

    This is a lightweight endpoint that just fetches log counts and severity distribution.

    Args:
        hours_back: Number of hours to look back (default: 24)

    Returns:
        Log statistics
    """
    try:
        from app.integrations.gcp import GCPLoggingClient

        logger.info(
            "Fetching quick log statistics",
            extra={"hours_back": hours_back}
        )

        client = GCPLoggingClient()
        stats = client.get_log_statistics(hours_back=hours_back)

        return {
            "success": True,
            "data": stats
        }

    except GCPIntegrationError as e:
        logger.error(
            "Failed to fetch log statistics",
            extra={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "Failed to fetch statistics",
                "message": e.message
            }
        )
    except Exception as e:
        logger.error(
            "Unexpected error fetching statistics",
            extra={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )
