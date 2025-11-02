"""
Test configuration and fixtures for the AI Database Query Agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.utils.config import Settings
from src.database.manager import DatabaseManager
from src.agents.workflow import DatabaseQueryWorkflow


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        openai_api_key="test_key",
        log_level="DEBUG",
        allow_write_operations=False,
        max_query_timeout=10
    )


@pytest.fixture
def mock_database_manager(mock_settings):
    """Create mock database manager for testing."""
    manager = Mock(spec=DatabaseManager)
    manager.settings = mock_settings
    manager.add_connection = AsyncMock(return_value=True)
    manager.get_schema_info = AsyncMock(return_value={})
    manager.execute_query = AsyncMock(return_value=[])
    return manager


@pytest.fixture
def mock_workflow(mock_settings):
    """Create mock workflow for testing."""
    workflow = Mock(spec=DatabaseQueryWorkflow)
    workflow.settings = mock_settings
    workflow.process_query = AsyncMock()
    return workflow


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_query_request():
    """Create sample query request for testing."""
    from src.models.query import QueryRequest
    return QueryRequest(
        query="Show me all users",
        connection_name="test_db",
        context={"user_role": "analyst"}
    )


@pytest.fixture
def sample_schema_info():
    """Create sample schema information for testing."""
    return {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "email", "type": "VARCHAR"}
                ]
            }
        ],
        "relationships": []
    }
