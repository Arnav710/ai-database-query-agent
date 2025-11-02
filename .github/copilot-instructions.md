<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI-Powered Database Query Agent - Copilot Instructions

## Project Overview
This is an AI-powered database query agent built with LangChain, LangGraph, and LangSmith. The system allows users to interact with databases using natural language queries.

## Architecture Guidelines
- Use multi-agent architecture with LangGraph for workflow orchestration
- Implement specialized agents for different responsibilities (schema analysis, query generation, safety validation, optimization, explanation)
- Use LangChain for database connectors and SQL toolkits
- Integrate LangSmith for monitoring, tracking, and continuous improvement

## Code Style & Patterns
- Follow Python PEP 8 conventions
- Use type hints throughout the codebase
- Implement proper error handling and logging
- Use Pydantic models for data validation
- Follow the repository pattern for database operations
- Use dependency injection for better testability

## Security Considerations
- Always validate SQL queries before execution
- Implement read-only access by default
- Use parameterized queries to prevent SQL injection
- Add rate limiting and timeout protection
- Log all database operations for audit purposes

## Testing Guidelines
- Write unit tests for individual agents and components
- Create integration tests for database connections
- Mock external API calls in tests
- Use pytest fixtures for test data setup
- Maintain high test coverage (>80%)

## Database Integration
- Support multiple database types (PostgreSQL, MySQL, SQLite, MongoDB)
- Use SQLAlchemy for SQL databases
- Implement proper connection pooling
- Handle database-specific SQL dialects
- Provide schema introspection capabilities

## Agent Responsibilities
1. **Schema Analyzer**: Database structure understanding and relationship mapping
2. **Query Generator**: Natural language to SQL conversion
3. **Safety Validator**: Query safety checks and permission validation
4. **Query Optimizer**: Performance analysis and optimization suggestions
5. **Result Explainer**: Human-readable query explanations

## API Design
- Use FastAPI for REST API endpoints
- Implement proper request/response models
- Add API documentation with OpenAPI/Swagger
- Include rate limiting and authentication
- Provide WebSocket support for real-time interactions

## Monitoring & Observability
- Use structured logging with appropriate log levels
- Implement metrics collection for query performance
- Track agent performance and accuracy
- Monitor database connection health
- Use LangSmith for conversation flow tracking
