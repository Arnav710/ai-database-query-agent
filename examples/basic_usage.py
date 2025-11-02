"""
Basic usage example for the AI Database Query Agent.

This example demonstrates how to:
1. Set up the agent
2. Connect to a database
3. Execute natural language queries
4. Handle responses and errors
"""

import asyncio
import os
from src.main import DatabaseQueryAgent
from src.utils.config import Settings


async def main():
    """Main example function."""
    
    # Initialize the agent with custom settings
    settings = Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your_api_key_here"),
        log_level="INFO",
        allow_write_operations=False,  # Safe mode for examples
        max_query_timeout=30
    )
    
    agent = DatabaseQueryAgent(settings)
    
    print("🤖 AI Database Query Agent - Basic Usage Example")
    print("=" * 50)
    
    # Example 1: Connect to SQLite database
    print("\n1. Connecting to database...")
    connection_success = await agent.connect_database(
        connection_string="sqlite:///example.db",
        connection_name="example_db"
    )
    
    if not connection_success:
        print("❌ Failed to connect to database")
        return
    
    print("✅ Successfully connected to database")
    
    # Example 2: Execute natural language queries
    example_queries = [
        "Show me all tables in the database",
        "Count the number of records in each table",
        "Find the most recent entries",
        "Show me the database schema"
    ]
    
    print("\n2. Executing example queries...")
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        try:
            response = await agent.query(query, "example_db")
            
            if response.success:
                print(f"✅ SQL Generated: {response.sql_query}")
                print(f"📝 Explanation: {response.explanation}")
                print(f"📊 Results: {len(response.results)} rows returned")
                
                # Show sample results
                if response.results:
                    print("📋 Sample data:")
                    for row in response.results[:3]:  # Show first 3 rows
                        print(f"   {row}")
                    if len(response.results) > 3:
                        print(f"   ... and {len(response.results) - 3} more rows")
            else:
                print(f"❌ Query failed: {response.error}")
                
        except Exception as e:
            print(f"❌ Error executing query: {e}")
    
    # Example 3: Schema exploration
    print("\n3. Exploring database schema...")
    
    try:
        schema_info = await agent.get_schema_info("example_db")
        print(f"📋 Schema information: {schema_info}")
    except Exception as e:
        print(f"❌ Error getting schema: {e}")
    
    # Example 4: List connections
    print("\n4. Listing database connections...")
    
    connections = await agent.list_connections()
    for name, info in connections.items():
        print(f"🔗 {name}: {info['database_type']} (Active: {info['is_active']})")
    
    # Cleanup
    print("\n5. Cleaning up...")
    await agent.disconnect_all()
    print("✅ Disconnected from all databases")


async def advanced_example():
    """Advanced usage example with context and conversation."""
    
    agent = DatabaseQueryAgent()
    
    print("\n🚀 Advanced Usage Example")
    print("=" * 30)
    
    # Connect to database
    await agent.connect_database("sqlite:///sales.db", "sales_db")
    
    # Example of conversational queries with context
    conversation_queries = [
        {
            "query": "Show me sales data for this month",
            "context": {"user_role": "sales_manager", "department": "sales"}
        },
        {
            "query": "Now show me the top 5 customers from those results",
            "context": {"previous_query": "sales data for this month"}
        },
        {
            "query": "What was their average order value?",
            "context": {"referring_to": "top 5 customers"}
        }
    ]
    
    for i, query_info in enumerate(conversation_queries, 1):
        print(f"\n--- Conversational Query {i} ---")
        print(f"Query: {query_info['query']}")
        print(f"Context: {query_info['context']}")
        
        response = await agent.query(
            query_info['query'], 
            "sales_db", 
            query_info['context']
        )
        
        if response.success:
            print(f"SQL: {response.sql_query}")
            print(f"Explanation: {response.explanation}")
        else:
            print(f"Error: {response.error}")
    
    await agent.disconnect_all()


if __name__ == "__main__":
    # Run basic example
    asyncio.run(main())
    
    # Uncomment to run advanced example
    # asyncio.run(advanced_example())
