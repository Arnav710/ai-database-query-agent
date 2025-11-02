"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from src.models.query import (
    QueryRequest, 
    QueryResponse, 
    DatabaseConnection,
    SafetyValidationResult,
    QueryOptimizationResult
)


def test_query_request_creation():
    """Test QueryRequest model creation."""
    request = QueryRequest(
        query="SELECT * FROM users",
        connection_name="test_db"
    )
    
    assert request.query == "SELECT * FROM users"
    assert request.connection_name == "test_db"
    assert request.context == {}


def test_query_response_creation():
    """Test QueryResponse model creation."""
    response = QueryResponse(
        success=True,
        sql_query="SELECT * FROM users",
        explanation="This query selects all users",
        results=[{"id": 1, "name": "John"}]
    )
    
    assert response.success is True
    assert response.sql_query == "SELECT * FROM users"
    assert len(response.results) == 1
    assert isinstance(response.timestamp, datetime)


def test_database_connection_creation():
    """Test DatabaseConnection model creation."""
    connection = DatabaseConnection(
        name="test_db",
        connection_string="postgresql://localhost/test",
        database_type="postgresql"
    )
    
    assert connection.name == "test_db"
    assert connection.database_type == "postgresql"
    assert connection.is_active is False
    assert isinstance(connection.created_at, datetime)


def test_safety_validation_result():
    """Test SafetyValidationResult model."""
    result = SafetyValidationResult(
        is_safe=False,
        issues=["Dangerous operation detected"],
        risk_level="high"
    )
    
    assert result.is_safe is False
    assert len(result.issues) == 1
    assert result.risk_level == "high"


def test_query_optimization_result():
    """Test QueryOptimizationResult model."""
    result = QueryOptimizationResult(
        optimized_query="SELECT id, name FROM users WHERE active = 1",
        suggestions=["Added WHERE clause for better performance"]
    )
    
    assert "WHERE active = 1" in result.optimized_query
    assert len(result.suggestions) == 1
