# OnCall Agent - GCP Log Analysis

An intelligent system that analyzes GCP Cloud Logs and generates detailed reports with AI-powered fix suggestions.

## Features

- 🔍 **GCP Cloud Logging Integration**: Fetch and analyze logs from Google Cloud Platform
- 🤖 **AI-Powered Analysis**: Use OpenAI GPT-4 or Anthropic Claude to analyze logs and identify issues
- 📊 **Detailed Reporting**: Generate comprehensive reports in Markdown or JSON format
- 🎯 **Smart Filtering**: Focus on errors/warnings or use custom log filters
- 💡 **Fix Suggestions**: Get actionable recommendations and code examples for identified issues
- 🚀 **FastAPI Backend**: High-performance async API with automatic OpenAPI documentation

## Quick Start

### Prerequisites

- Python 3.11 or higher
- GCP project with Cloud Logging enabled
- GCP service account with logging read permissions
- OpenAI API key or Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd oncall-agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/base.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required configuration:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_CREDENTIALS_JSON`: Path to your GCP service account credentials
   - `OPENAI_API_KEY`: Your OpenAI API key (or `ANTHROPIC_API_KEY` for Claude)

### Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage

### Analyze Logs via API

**Basic analysis (errors from last 24 hours):**

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/" \
  -H "Content-Type: application/json" \
  -d '{
    "hours_back": 24,
    "focus_on_errors": true,
    "output_format": "markdown"
  }'
```

**Custom analysis with filter:**

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/" \
  -H "Content-Type: application/json" \
  -d '{
    "hours_back": 12,
    "filter_query": "resource.type=\"k8s_container\" AND severity >= \"ERROR\"",
    "max_logs": 100,
    "focus_on_errors": true,
    "output_format": "json"
  }'
```

**Get quick statistics:**

```bash
curl "http://localhost:8000/api/v1/analysis/quick-stats?hours_back=24"
```

### Response Format

The analysis endpoint returns a comprehensive report including:

```json
{
  "analysis_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "statistics": {
    "total_logs": 150,
    "by_severity": {
      "ERROR": 45,
      "WARNING": 30,
      "INFO": 75
    },
    "time_range_hours": 24,
    "most_common_errors": ["Database connection failed", "API timeout"]
  },
  "findings": [
    {
      "severity": "critical",
      "title": "Database Connection Failures",
      "description": "Multiple instances of database connection failures...",
      "affected_logs_count": 15,
      "suggested_fix": "Check database credentials and increase connection pool size",
      "code_example": "db_config = {'pool_size': 20, 'max_overflow': 10}"
    }
  ],
  "summary": "Analysis identified 3 critical issues...",
  "document_path": "/path/to/analysis_report.md",
  "recommendations": [
    "Implement database connection retry logic",
    "Set up monitoring for error rates"
  ]
}
```

### Generated Reports

Analysis reports are saved to the `analysis_reports/` directory (configurable via `ANALYSIS_OUTPUT_DIR`).

**Markdown format** includes:
- Executive summary
- Log statistics
- Detailed findings with severity levels
- Suggested fixes and code examples
- General recommendations

**JSON format** provides the same information in a structured format for programmatic processing.

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | GCP project ID | Required |
| `GCP_CREDENTIALS_JSON` | Path to service account credentials | Required |
| `GCP_LOG_FILTER` | Default Cloud Logging filter | "" |
| `GCP_LOG_LIMIT` | Max logs per request | 100 |
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | openai |
| `LLM_MODEL` | Model to use | gpt-4 |
| `OPENAI_API_KEY` | OpenAI API key | Required if using OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required if using Anthropic |
| `ANALYSIS_OUTPUT_DIR` | Report output directory | analysis_reports |
| `MAX_LOG_ENTRIES_TO_ANALYZE` | Max logs sent to LLM | 50 |

### GCP Setup

1. **Create a service account:**
   ```bash
   gcloud iam service-accounts create oncall-agent \
     --display-name="OnCall Agent Log Reader"
   ```

2. **Grant logging permissions:**
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:oncall-agent@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/logging.viewer"
   ```

3. **Create and download credentials:**
   ```bash
   gcloud iam service-accounts keys create credentials.json \
     --iam-account=oncall-agent@PROJECT_ID.iam.gserviceaccount.com
   ```

### GCP Log Filters

Use Cloud Logging filter syntax for `filter_query`:

```
# Kubernetes errors only
resource.type="k8s_container" AND severity >= "ERROR"

# Specific service errors
resource.labels.service_name="my-service" AND severity="ERROR"

# Time-based with severity
timestamp >= "2024-01-01T00:00:00Z" AND severity >= "WARNING"

# Text search in logs
textPayload=~"database.*connection.*failed"
```

## Development

### Install development dependencies

```bash
pip install -r requirements/dev.txt
```

### Run tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_gcp_integration.py
```

### Code formatting and linting

```bash
# Format code
black app tests

# Sort imports
isort app tests

# Lint
ruff check app tests

# Type check
mypy app
```

### Project Structure

```
oncall-agent/
├── app/
│   ├── api/              # FastAPI routes
│   ├── core/             # Core utilities (config, logging)
│   ├── integrations/     # External integrations (GCP)
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # Application entry point
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── requirements/         # Python dependencies
├── .env.example          # Example environment configuration
└── README.md             # This file
```

## API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.

## Troubleshooting

### Common Issues

**"GCP_PROJECT_ID_MISSING" error:**
- Ensure `GCP_PROJECT_ID` is set in your `.env` file

**"Failed to initialize GCP Logging client":**
- Verify your service account credentials are correct
- Check that the service account has `roles/logging.viewer` permissions
- Ensure the credentials file path is correct

**"LLM_INIT_ERROR":**
- Verify your OpenAI or Anthropic API key is set correctly
- Check that you have sufficient API credits

**No logs returned:**
- Verify logs exist in your GCP project for the specified time range
- Check your `GCP_LOG_FILTER` if set
- Try increasing `hours_back` parameter

## Architecture

This application follows a clean architecture pattern:

1. **API Layer** (`app/api`): FastAPI endpoints for HTTP requests
2. **Service Layer** (`app/services`): Business logic and orchestration
3. **Integration Layer** (`app/integrations`): External service clients
4. **Core Layer** (`app/core`): Shared utilities and configuration

The log analysis workflow:
1. API receives request → validates with Pydantic
2. Service fetches logs from GCP Cloud Logging
3. Service sends logs to LLM for analysis
4. LLM returns structured findings
5. Service generates report document
6. API returns complete analysis

## Contributing

1. Follow the guidelines in `CLAUDE.md`
2. Write tests for new features
3. Ensure code passes linting and type checking
4. Update documentation as needed

## License

[Your License Here]

## Support

For issues, questions, or contributions, please open an issue on GitHub.
