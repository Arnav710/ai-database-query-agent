# API Documentation

## Overview

The AI-Powered Database Query Agent provides a REST API for natural language database querying. This document describes the available endpoints and their usage.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

API keys are required for all requests. Include your API key in the header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### POST /query

Execute a natural language database query.

**Request Body:**
```json
{
  "query": "Show me the top 10 customers by revenue",
  "connection_name": "production_db",
  "context": {
    "user_role": "analyst",
    "department": "sales"
  }
}
```

**Response:**
```json
{
  "success": true,
  "sql_query": "SELECT customer_name, SUM(revenue) as total_revenue FROM customers JOIN orders ON customers.id = orders.customer_id GROUP BY customer_name ORDER BY total_revenue DESC LIMIT 10",
  "explanation": "This query finds the top 10 customers by total revenue by joining the customers and orders tables, grouping by customer name, and sorting by total revenue in descending order.",
  "results": [
    {
      "customer_name": "Acme Corp",
      "total_revenue": 150000.00
    }
  ],
  "metadata": {
    "execution_time": 0.145,
    "optimization_suggestions": []
  },
  "timestamp": "2025-11-02T10:30:00Z"
}
```

### GET /connections

List available database connections.

**Response:**
```json
{
  "connections": {
    "production_db": {
      "database_type": "postgresql",
      "is_active": true,
      "created_at": "2025-11-02T09:00:00Z"
    }
  }
}
```

### POST /connections

Add a new database connection.

**Request Body:**
```json
{
  "name": "analytics_db",
  "connection_string": "postgresql://user:pass@localhost/analytics",
  "description": "Analytics database connection"
}
```

### GET /schema/{connection_name}

Get schema information for a specific database connection.

**Response:**
```json
{
  "tables": [
    {
      "name": "users",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "nullable": false
        }
      ]
    }
  ],
  "relationships": []
}
```

### POST /explain

Get explanation for a SQL query without executing it.

**Request Body:**
```json
{
  "sql_query": "SELECT * FROM users WHERE created_at > '2023-01-01'",
  "connection_name": "production_db"
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "error": "Error message description",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "query",
    "message": "Query cannot be empty"
  }
}
```

## Rate Limiting

API requests are limited to:
- 60 requests per minute per API key
- 1000 requests per hour per API key

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## WebSocket API

For real-time query execution and streaming results:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/query');

ws.send(JSON.stringify({
  "query": "Show me recent orders",
  "connection_name": "production_db"
}));

ws.onmessage = function(event) {
  const response = JSON.parse(event.data);
  console.log(response);
};
```
