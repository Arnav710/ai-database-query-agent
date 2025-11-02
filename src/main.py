"""
AI-Powered Database Query Agent

Main application entry point for the database query agent system.
"""

from typing import Optional, Dict, Any
import logging
from src.agents.workflow import DatabaseQueryWorkflow
from src.database.manager import DatabaseManager
from src.models.query import QueryRequest, QueryResponse
from src.utils.config import Settings

logger = logging.getLogger(__name__)


class DatabaseQueryAgent:
    """
    Main interface for the AI-Powered Database Query Agent.
    
    This class orchestrates the multi-agent workflow to process natural language
    queries and generate SQL responses with explanations and safety validation.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the database query agent."""
        self.settings = settings or Settings()
        self.db_manager = DatabaseManager(self.settings)
        self.workflow = DatabaseQueryWorkflow(self.settings)
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the application."""
        logging.basicConfig(
            level=getattr(logging, self.settings.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def connect_database(self, connection_string: str, connection_name: str = "default") -> bool:
        """
        Connect to a database using the provided connection string.
        
        Args:
            connection_string: Database connection string
            connection_name: Name to identify this connection
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            return await self.db_manager.add_connection(connection_name, connection_string)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    async def query(self, 
                   natural_language_query: str, 
                   connection_name: str = "default",
                   context: Optional[Dict[str, Any]] = None) -> QueryResponse:
        """
        Process a natural language query and return SQL with results.
        
        Args:
            natural_language_query: User's question in natural language
            connection_name: Database connection to use
            context: Additional context for the query
            
        Returns:
            QueryResponse: Generated SQL, explanation, and results
        """
        try:
            request = QueryRequest(
                query=natural_language_query,
                connection_name=connection_name,
                context=context or {}
            )
            
            return await self.workflow.process_query(request)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResponse(
                success=False,
                error=str(e),
                sql_query="",
                explanation="Failed to process query",
                results=[]
            )
    
    async def get_schema_info(self, connection_name: str = "default") -> Dict[str, Any]:
        """
        Get schema information for the specified database connection.
        
        Args:
            connection_name: Database connection name
            
        Returns:
            Dict containing schema information
        """
        return await self.db_manager.get_schema_info(connection_name)
    
    async def list_connections(self) -> Dict[str, Dict[str, Any]]:
        """List all available database connections."""
        return self.db_manager.list_connections()
    
    async def disconnect(self, connection_name: str = "default") -> bool:
        """Disconnect from a specific database."""
        return await self.db_manager.remove_connection(connection_name)
    
    async def disconnect_all(self):
        """Disconnect from all databases."""
        await self.db_manager.close_all_connections()


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Example usage
        agent = DatabaseQueryAgent()
        
        # Connect to a database
        success = await agent.connect_database(
            "sqlite:///example.db", 
            "example"
        )
        
        if success:
            # Query the database
            response = await agent.query(
                "Show me all users who registered last week",
                "example"
            )
            
            print(f"SQL Query: {response.sql_query}")
            print(f"Explanation: {response.explanation}")
            print(f"Results: {response.results}")
        
        # Clean up
        await agent.disconnect_all()
    
    asyncio.run(main())
