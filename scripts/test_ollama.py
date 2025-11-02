#!/usr/bin/env python3
"""
Test script for Ollama integration with the AI Database Query Agent.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import Settings
from src.utils.llm_factory import LLMFactory
from src.agents.query_generator import QueryGeneratorAgent


async def test_ollama_integration():
    """Test the Ollama integration."""
    print("🧪 Testing Ollama Integration")
    print("=" * 40)
    
    # Create settings for Ollama
    settings = Settings(
        llm_provider="ollama",
        ollama_base_url="http://localhost:11434",
        ollama_model="codellama:7b",
        temperature=0.1,
        max_tokens=500
    )
    
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"Ollama Model: {settings.ollama_model}")
    print(f"Base URL: {settings.ollama_base_url}")
    
    # Test LLM connection
    print("\n🔍 Testing LLM connection...")
    if LLMFactory.test_connection(settings):
        print("✅ LLM connection successful!")
    else:
        print("❌ LLM connection failed!")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Check if the model is installed: ollama list")
        print("3. Download the model if needed: ollama pull codellama:7b")
        return False
    
    # Test Query Generator
    print("\n🤖 Testing Query Generator Agent...")
    try:
        agent = QueryGeneratorAgent(settings)
        
        # Sample schema
        sample_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True},
                        {"name": "name", "type": "VARCHAR(100)"},
                        {"name": "email", "type": "VARCHAR(255)"},
                        {"name": "created_at", "type": "TIMESTAMP"}
                    ]
                },
                {
                    "name": "orders",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True},
                        {"name": "user_id", "type": "INTEGER", "foreign_key": "users.id"},
                        {"name": "amount", "type": "DECIMAL(10,2)"},
                        {"name": "order_date", "type": "TIMESTAMP"}
                    ]
                }
            ]
        }
        
        # Test queries
        test_queries = [
            "Show me all users",
            "Find users who have placed orders",
            "Get the total order amount for each user"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test Query {i}: {query} ---")
            
            try:
                sql = await agent.generate(query, sample_schema)
                print(f"Generated SQL: {sql}")
                
                if sql and "SELECT" in sql.upper():
                    print("✅ Query generation successful!")
                else:
                    print("⚠️  Query generation may have issues")
                    
            except Exception as e:
                print(f"❌ Query generation failed: {e}")
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_ollama_integration())
    sys.exit(0 if success else 1)
