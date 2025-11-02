"""
Database Manager for handling multiple database connections.

This module provides a centralized way to manage database connections,
schema information, and query execution across different database types.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.engine import Engine
from pymongo import MongoClient
import sqlite3
import logging
from src.models.query import DatabaseConnection, SchemaInfo
from src.utils.config import Settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages multiple database connections and provides unified interface
    for schema inspection and query execution.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connections: Dict[str, DatabaseConnection] = {}
        self.engines: Dict[str, Engine] = {}
        self.mongo_clients: Dict[str, MongoClient] = {}
    
    async def add_connection(self, name: str, connection_string: str) -> bool:
        """
        Add a new database connection.
        
        Args:
            name: Connection name identifier
            connection_string: Database connection string
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Determine database type from connection string
            db_type = self._get_database_type(connection_string)
            
            if db_type == "mongodb":
                client = MongoClient(connection_string)
                # Test connection
                client.admin.command('ping')
                self.mongo_clients[name] = client
            else:
                # SQL databases
                engine = create_engine(connection_string)
                # Test connection
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
                self.engines[name] = engine
            
            # Store connection info
            self.connections[name] = DatabaseConnection(
                name=name,
                connection_string=connection_string,
                database_type=db_type,
                is_active=True
            )
            
            logger.info(f"Successfully connected to database: {name} ({db_type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database {name}: {e}")
            return False
    
    def _get_database_type(self, connection_string: str) -> str:
        """Determine database type from connection string."""
        if connection_string.startswith("postgresql://"):
            return "postgresql"
        elif connection_string.startswith("mysql://"):
            return "mysql"
        elif connection_string.startswith("sqlite://"):
            return "sqlite"
        elif connection_string.startswith("mongodb://"):
            return "mongodb"
        else:
            return "unknown"
    
    async def get_schema_info(self, connection_name: str) -> Dict[str, Any]:
        """
        Get comprehensive schema information for a database.
        
        Args:
            connection_name: Name of the database connection
            
        Returns:
            Dict containing schema information
        """
        if connection_name not in self.connections:
            raise ValueError(f"Connection {connection_name} not found")
        
        connection = self.connections[connection_name]
        
        if connection.database_type == "mongodb":
            return await self._get_mongo_schema_info(connection_name)
        else:
            return await self._get_sql_schema_info(connection_name)
    
    async def _get_sql_schema_info(self, connection_name: str) -> Dict[str, Any]:
        """Get schema information for SQL databases."""
        engine = self.engines[connection_name]
        inspector = inspect(engine)
        
        schema_info = {
            "tables": [],
            "views": [],
            "relationships": [],
            "indexes": []
        }
        
        try:
            # Get table information
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                primary_keys = inspector.get_pk_constraint(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                indexes = inspector.get_indexes(table_name)
                
                table_info = {
                    "name": table_name,
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys,
                    "indexes": indexes
                }
                schema_info["tables"].append(table_info)
            
            # Get view information
            try:
                for view_name in inspector.get_view_names():
                    view_info = {
                        "name": view_name,
                        "columns": inspector.get_columns(view_name)
                    }
                    schema_info["views"].append(view_info)
            except Exception as e:
                logger.warning(f"Could not retrieve views: {e}")
            
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
        
        return schema_info
    
    async def _get_mongo_schema_info(self, connection_name: str) -> Dict[str, Any]:
        """Get schema information for MongoDB."""
        client = self.mongo_clients[connection_name]
        
        schema_info = {
            "databases": [],
            "collections": [],
            "sample_documents": {}
        }
        
        try:
            # Get database names
            db_names = client.list_database_names()
            schema_info["databases"] = db_names
            
            # For each database, get collection info
            for db_name in db_names:
                if db_name not in ["admin", "local", "config"]:
                    db = client[db_name]
                    collections = db.list_collection_names()
                    
                    for collection_name in collections:
                        collection = db[collection_name]
                        # Get sample document to understand schema
                        sample_doc = collection.find_one()
                        
                        collection_info = {
                            "database": db_name,
                            "name": collection_name,
                            "document_count": collection.count_documents({}),
                            "sample_fields": list(sample_doc.keys()) if sample_doc else []
                        }
                        schema_info["collections"].append(collection_info)
                        
                        if sample_doc:
                            schema_info["sample_documents"][f"{db_name}.{collection_name}"] = sample_doc
        
        except Exception as e:
            logger.error(f"Error getting MongoDB schema info: {e}")
        
        return schema_info
    
    async def execute_query(self, connection_name: str, query: str) -> List[Dict[str, Any]]:
        """
        Execute a query against the specified database.
        
        Args:
            connection_name: Name of the database connection
            query: SQL query to execute
            
        Returns:
            List of result dictionaries
        """
        if connection_name not in self.connections:
            raise ValueError(f"Connection {connection_name} not found")
        
        connection = self.connections[connection_name]
        
        if connection.database_type == "mongodb":
            raise NotImplementedError("MongoDB query execution not yet implemented")
        
        engine = self.engines[connection_name]
        results = []
        
        try:
            with engine.connect() as conn:
                result = conn.execute(query)
                if result.returns_rows:
                    columns = result.keys()
                    for row in result:
                        results.append(dict(zip(columns, row)))
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        
        return results
    
    def list_connections(self) -> Dict[str, Dict[str, Any]]:
        """List all available database connections."""
        return {
            name: {
                "database_type": conn.database_type,
                "is_active": conn.is_active,
                "created_at": conn.created_at,
                "last_used": conn.last_used
            }
            for name, conn in self.connections.items()
        }
    
    async def remove_connection(self, connection_name: str) -> bool:
        """Remove a database connection."""
        try:
            if connection_name in self.engines:
                self.engines[connection_name].dispose()
                del self.engines[connection_name]
            
            if connection_name in self.mongo_clients:
                self.mongo_clients[connection_name].close()
                del self.mongo_clients[connection_name]
            
            if connection_name in self.connections:
                del self.connections[connection_name]
            
            logger.info(f"Removed connection: {connection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing connection {connection_name}: {e}")
            return False
    
    async def close_all_connections(self):
        """Close all database connections."""
        for name in list(self.connections.keys()):
            await self.remove_connection(name)
