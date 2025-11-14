# CLAUDE.md - OnCall Agent Project Guide

This document provides comprehensive guidance for AI assistants working on the OnCall Agent codebase. It covers the project structure, development workflows, and key conventions to follow.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Development Workflows](#development-workflows)
4. [Key Conventions](#key-conventions)
5. [Testing Strategy](#testing-strategy)
6. [Deployment & Operations](#deployment--operations)
7. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Overview

### Purpose
OnCall Agent is an intelligent system designed to handle on-call operations, incident management, and automated response workflows. The system aims to reduce the burden on human operators by automating common incident response patterns and providing intelligent assistance during critical situations.

### Key Capabilities
- **Incident Detection**: Monitor systems and detect anomalies/incidents
- **Alert Management**: Receive, prioritize, and route alerts
- **Automated Response**: Execute predefined runbooks and remediation steps
- **Escalation Logic**: Intelligent escalation based on severity and response times
- **Communication**: Interface with chat platforms, ticketing systems, and paging services
- **Learning & Adaptation**: Learn from past incidents to improve responses

### Technology Stack
- **Language**: TypeScript/Node.js (primary), Python (for ML/data processing)
- **Framework**: Express.js or Fastify for API services
- **Database**: PostgreSQL (relational data), Redis (caching/queues)
- **Message Queue**: RabbitMQ or Kafka for event processing
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Kubernetes
- **CI/CD**: GitHub Actions

---

## Codebase Architecture

### Directory Structure

```
oncall-agent/
├── src/
│   ├── agent/               # Core agent logic
│   │   ├── brain.ts        # Decision-making engine
│   │   ├── memory.ts       # State and context management
│   │   └── actions/        # Available actions the agent can take
│   ├── integrations/        # External service integrations
│   │   ├── pagerduty/      # PagerDuty integration
│   │   ├── slack/          # Slack integration
│   │   ├── jira/           # Jira integration
│   │   └── monitoring/     # Prometheus, Datadog, etc.
│   ├── api/                 # REST/GraphQL API endpoints
│   │   ├── routes/         # Route definitions
│   │   ├── controllers/    # Request handlers
│   │   └── middleware/     # Auth, validation, etc.
│   ├── services/            # Business logic layer
│   │   ├── incident.ts     # Incident management
│   │   ├── alert.ts        # Alert processing
│   │   ├── runbook.ts      # Runbook execution
│   │   └── escalation.ts   # Escalation logic
│   ├── models/              # Data models and schemas
│   │   ├── incident.ts
│   │   ├── alert.ts
│   │   └── user.ts
│   ├── database/            # Database setup and migrations
│   │   ├── migrations/
│   │   └── seeds/
│   ├── workers/             # Background job processors
│   │   ├── alert-processor.ts
│   │   └── health-check.ts
│   ├── utils/               # Shared utilities
│   │   ├── logger.ts
│   │   ├── config.ts
│   │   └── validation.ts
│   └── types/               # TypeScript type definitions
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── docs/                    # Additional documentation
│   ├── architecture.md
│   ├── api.md
│   └── runbooks/
├── scripts/                 # Build and deployment scripts
├── config/                  # Configuration files
│   ├── development.json
│   ├── staging.json
│   └── production.json
├── .github/
│   └── workflows/          # CI/CD pipelines
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── package.json
├── tsconfig.json
├── .eslintrc.js
├── .prettierrc
└── CLAUDE.md               # This file
```

### Core Components

#### 1. Agent Brain (`src/agent/brain.ts`)
The decision-making engine that:
- Analyzes incoming alerts and incidents
- Determines appropriate actions based on context
- Manages agent state and decision history
- Coordinates with external services

#### 2. Integrations (`src/integrations/`)
Each integration follows a standard interface:
```typescript
interface Integration {
  name: string;
  initialize(): Promise<void>;
  handleEvent(event: Event): Promise<Response>;
  executeAction(action: Action): Promise<Result>;
}
```

#### 3. Services Layer (`src/services/`)
Business logic that:
- Processes incidents through their lifecycle
- Executes runbooks and automated remediation
- Manages escalations and notifications
- Maintains audit logs

#### 4. API Layer (`src/api/`)
RESTful API with endpoints for:
- Webhook receivers (alerts from monitoring systems)
- Configuration management
- Incident query and updates
- Admin operations

---

## Development Workflows

### Getting Started

```bash
# Clone the repository
git clone <repository-url>
cd oncall-agent

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Set up database
npm run db:migrate
npm run db:seed

# Run in development mode
npm run dev

# Run tests
npm test
```

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Individual feature branches
- **fix/***: Bug fix branches
- **hotfix/***: Critical production fixes
- **claude/***: AI-assisted development branches (auto-generated)

### Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Test additions or modifications
- **chore**: Build process or auxiliary tool changes

Examples:
```
feat(agent): add intelligent alert deduplication
fix(slack): resolve message formatting issue
docs(readme): update installation instructions
```

### Code Review Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Ensure CI passes (linting, tests, build)
4. Create pull request with detailed description
5. Address review comments
6. Merge after approval

---

## Key Conventions

### TypeScript Standards

1. **Strict Mode**: Always use TypeScript strict mode
   ```json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true,
       "strictNullChecks": true
     }
   }
   ```

2. **Type Definitions**: Prefer interfaces over types for objects
   ```typescript
   // Good
   interface Alert {
     id: string;
     severity: Severity;
     timestamp: Date;
   }

   // Avoid for objects
   type Alert = {
     id: string;
     severity: Severity;
     timestamp: Date;
   }
   ```

3. **Avoid `any`**: Use `unknown` or proper typing
   ```typescript
   // Bad
   function processData(data: any) { }

   // Good
   function processData(data: unknown) {
     if (isAlert(data)) {
       // Process alert
     }
   }
   ```

### Error Handling

1. **Use Custom Error Classes**:
   ```typescript
   class IncidentError extends Error {
     constructor(
       message: string,
       public code: string,
       public context?: Record<string, unknown>
     ) {
       super(message);
       this.name = 'IncidentError';
     }
   }
   ```

2. **Async Error Handling**:
   ```typescript
   try {
     const result = await riskyOperation();
     return { success: true, data: result };
   } catch (error) {
     logger.error('Operation failed', { error, context });
     throw new IncidentError('Failed to process', 'PROCESS_ERROR', { error });
   }
   ```

3. **Never Swallow Errors**: Always log or re-throw
   ```typescript
   // Bad
   try {
     await operation();
   } catch (e) {
     // Silent failure
   }

   // Good
   try {
     await operation();
   } catch (error) {
     logger.error('Operation failed', { error });
     throw error;
   }
   ```

### Logging

Use structured logging with context:

```typescript
import { logger } from '@/utils/logger';

// Include context in all logs
logger.info('Processing alert', {
  alertId: alert.id,
  severity: alert.severity,
  source: alert.source
});

// Log levels:
// - error: Errors that require attention
// - warn: Warning conditions
// - info: Informational messages
// - debug: Debug information (development only)
```

### Configuration Management

1. **Environment Variables**: Use for secrets and environment-specific values
2. **Config Files**: Use for application settings
3. **Never Commit Secrets**: Use `.env` files (gitignored)

```typescript
// config/index.ts
import dotenv from 'dotenv';

dotenv.config();

export const config = {
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    password: process.env.DB_PASSWORD, // Required
  },
  agent: {
    checkInterval: 60000, // Can be overridden by env
    maxConcurrentIncidents: 10,
  }
};
```

### Database Conventions

1. **Migrations**: Always use migrations for schema changes
2. **Timestamps**: Include `created_at` and `updated_at` on all tables
3. **Soft Deletes**: Use `deleted_at` instead of hard deletes
4. **Transactions**: Use transactions for multi-step operations

```typescript
// Use transactions for related operations
await db.transaction(async (trx) => {
  await trx('incidents').insert(incident);
  await trx('alerts').where({ id: alertId }).update({ incident_id: incident.id });
  await trx('audit_log').insert({ action: 'incident_created', incident_id: incident.id });
});
```

### API Design

1. **RESTful Conventions**: Follow REST principles
   - GET: Retrieve resources
   - POST: Create resources
   - PUT/PATCH: Update resources
   - DELETE: Remove resources

2. **Versioning**: Version the API (`/api/v1/...`)

3. **Response Format**:
   ```typescript
   // Success
   {
     "success": true,
     "data": { /* resource */ },
     "meta": { /* pagination, etc */ }
   }

   // Error
   {
     "success": false,
     "error": {
       "code": "ERROR_CODE",
       "message": "Human-readable message",
       "details": { /* additional context */ }
     }
   }
   ```

4. **Status Codes**:
   - 200: Success
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found
   - 500: Internal Server Error

---

## Testing Strategy

### Test Pyramid

1. **Unit Tests** (70%): Test individual functions and classes
2. **Integration Tests** (20%): Test component interactions
3. **E2E Tests** (10%): Test complete workflows

### Testing Tools

- **Framework**: Jest
- **Mocking**: Jest mocks, sinon
- **API Testing**: Supertest
- **Coverage**: Istanbul (via Jest)

### Test Structure

```typescript
describe('AlertService', () => {
  describe('processAlert', () => {
    it('should create incident for critical alert', async () => {
      // Arrange
      const alert = createMockAlert({ severity: 'critical' });

      // Act
      const result = await alertService.processAlert(alert);

      // Assert
      expect(result.incidentCreated).toBe(true);
      expect(result.incident.severity).toBe('critical');
    });

    it('should deduplicate similar alerts', async () => {
      // Test deduplication logic
    });
  });
});
```

### Coverage Requirements

- **Minimum**: 80% code coverage
- **Critical Paths**: 100% coverage for core agent logic
- **Run Coverage**: `npm run test:coverage`

### Testing Best Practices

1. **Isolated Tests**: Each test should be independent
2. **Mock External Services**: Don't call real APIs in tests
3. **Clear Naming**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **Test Edge Cases**: Include error conditions and edge cases

---

## Deployment & Operations

### Environments

1. **Development**: Local development environment
2. **Staging**: Pre-production testing
3. **Production**: Live environment

### Deployment Process

```bash
# Build
npm run build

# Run migrations
npm run db:migrate:production

# Start application
npm start
```

### Health Checks

The application exposes health check endpoints:
- `/health`: Basic health check
- `/health/ready`: Readiness probe (includes DB connectivity)
- `/health/live`: Liveness probe

### Monitoring

1. **Metrics**: Exposed via `/metrics` endpoint (Prometheus format)
2. **Logging**: Structured JSON logs to stdout
3. **Tracing**: Distributed tracing with correlation IDs
4. **Alerts**: Set up alerts for critical metrics

### Environment Variables

Required environment variables:
```
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
LOG_LEVEL=info

# Integration credentials
PAGERDUTY_API_KEY=...
SLACK_BOT_TOKEN=...
SLACK_SIGNING_SECRET=...
```

---

## AI Assistant Guidelines

### When Working on This Codebase

#### 1. Understanding Context

Before making changes:
- Read relevant code sections thoroughly
- Understand the data flow and dependencies
- Check for existing patterns and conventions
- Review related tests

#### 2. Making Changes

**Always:**
- Follow existing code patterns and style
- Write or update tests for your changes
- Update documentation if behavior changes
- Use TypeScript strictly (no `any` types)
- Add appropriate error handling
- Include logging for important operations

**Never:**
- Commit secrets or credentials
- Break existing tests without fixing them
- Make breaking API changes without discussion
- Skip error handling
- Use `console.log` (use the logger instead)
- Disable linting rules without good reason

#### 3. Code Quality Checklist

Before committing:
- [ ] Code follows TypeScript best practices
- [ ] All tests pass (`npm test`)
- [ ] Linting passes (`npm run lint`)
- [ ] Type checking passes (`npm run typecheck`)
- [ ] No security vulnerabilities introduced
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Documentation is updated

#### 4. Common Tasks

**Adding a New Integration:**
1. Create directory in `src/integrations/<service>/`
2. Implement the `Integration` interface
3. Add configuration in `config/`
4. Write integration tests
5. Update documentation

**Adding a New API Endpoint:**
1. Define route in `src/api/routes/`
2. Implement controller in `src/api/controllers/`
3. Add request validation middleware
4. Write tests for all scenarios
5. Document the endpoint in `docs/api.md`

**Modifying Database Schema:**
1. Create migration file: `npm run db:migration:create <name>`
2. Write both `up` and `down` migrations
3. Test migration locally
4. Update model files
5. Update affected tests

#### 5. Security Considerations

Always consider:
- **Input Validation**: Validate all external input
- **SQL Injection**: Use parameterized queries
- **XSS**: Sanitize user input in responses
- **Authentication**: Verify user permissions
- **Rate Limiting**: Implement rate limits on public endpoints
- **Secrets Management**: Never hardcode secrets
- **Dependency Security**: Keep dependencies updated

#### 6. Performance Considerations

- **Database**: Use indexes, avoid N+1 queries
- **Caching**: Cache frequently accessed data
- **Async Operations**: Use async/await properly
- **Memory**: Be mindful of memory leaks
- **Rate Limits**: Respect external API rate limits

#### 7. Debugging Tips

When investigating issues:
1. Check logs first (structured logging helps)
2. Use correlation IDs to trace requests
3. Verify configuration and environment variables
4. Test integrations individually
5. Use debugging tools (VS Code debugger, Chrome DevTools)
6. Check metrics and monitoring dashboards

#### 8. Common Patterns

**Retry Logic:**
```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(Math.pow(2, i) * 1000);
    }
  }
  throw new Error('Max retries exceeded');
}
```

**Circuit Breaker:**
```typescript
// Use circuit breaker for external services
const breaker = new CircuitBreaker(externalService.call, {
  timeout: 5000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
});
```

**Rate Limiting:**
```typescript
// Apply rate limiting to public endpoints
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

#### 9. Integration-Specific Guidelines

**Slack Integration:**
- Use Block Kit for rich messages
- Handle rate limits (1 message per second per channel)
- Verify request signatures
- Use threads for related messages

**PagerDuty Integration:**
- Deduplicate incidents using `dedup_key`
- Map severity levels correctly
- Include relevant context in incidents
- Handle webhook retries

**Monitoring Integration:**
- Use consistent metric names
- Add labels for filtering
- Set appropriate alert thresholds
- Document custom metrics

#### 10. Escalation Patterns

When you encounter:
- **Unclear Requirements**: Ask for clarification before implementing
- **Breaking Changes**: Discuss with the team first
- **Security Concerns**: Flag immediately and don't proceed
- **Performance Issues**: Profile and measure before optimizing
- **Complex Decisions**: Document trade-offs and rationale

---

## Additional Resources

### Documentation
- `docs/architecture.md`: Detailed architecture overview
- `docs/api.md`: Complete API reference
- `docs/runbooks/`: Operational runbooks

### External References
- [TypeScript Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [REST API Design](https://restfulapi.net/)

### Team Contacts
- **Architecture Questions**: Check `docs/architecture.md`
- **API Questions**: Check `docs/api.md`
- **DevOps**: Check deployment documentation

---

## Changelog

### Version History

**v1.0.0 - 2025-11-14**
- Initial CLAUDE.md creation
- Established project structure and conventions
- Defined AI assistant guidelines

---

## Contributing

When contributing to this project:

1. Read this entire document
2. Set up your development environment
3. Create a feature branch
4. Follow all conventions and guidelines
5. Write comprehensive tests
6. Submit a pull request with clear description

Remember: Quality over speed. Well-tested, maintainable code is always preferred over quick but fragile solutions.

---

**Last Updated**: 2025-11-14
**Maintainers**: OnCall Agent Team
**Version**: 1.0.0
