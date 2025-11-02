"""
Query Generator Agent

This agent converts natural language queries into SQL using
the schema context provided by the Schema Analyzer Agent.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from src.utils.config import Settings
from src.utils.llm_factory import LLMFactory
import logging

logger = logging.getLogger(__name__)


class QueryGeneratorAgent:
    """
    Agent responsible for converting natural language queries to SQL
    using database schema context and business logic understanding.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        # Use the factory to create the appropriate LLM based on configuration
        self.llm = LLMFactory.create_llm(settings)
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Set up prompt templates for query generation."""
        self.generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SQL query generator. Convert natural language 
            questions into accurate, efficient SQL queries based on the provided database schema.
            
            Guidelines:
            1. Use proper SQL syntax and best practices
            2. Consider table relationships and join strategies
            3. Include appropriate WHERE clauses for filtering
            4. Use proper aggregation functions when needed
            5. Optimize for performance with indexes and constraints
            6. Return ONLY the SQL query, no explanations or markdown formatting
            7. Do not include ```sql``` code blocks in your response
            
            Database Schema: {schema_info}"""),
            ("human", "Natural Language Query: {user_query}\n\nAdditional Context: {context}")
        ])
    
    async def generate(self, 
                      user_query: str, 
                      schema_info: Dict[str, Any], 
                      context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate SQL query from natural language input.
        
        Args:
            user_query: Natural language query from user
            schema_info: Database schema information
            context: Additional context for query generation
            
        Returns:
            Generated SQL query string
        """
        try:
            logger.info(f"Generating SQL for query: {user_query[:100]}...")
            logger.info(f"Using LLM provider: {self.settings.llm_provider}")
            
            # Format the prompt with schema and query information
            formatted_prompt = self.generation_prompt.format_messages(
                schema_info=schema_info,
                user_query=user_query,
                context=context or {}
            )
            
            # Generate SQL using LLM
            response = await self.llm.ainvoke(formatted_prompt)
            sql_query = self._clean_sql_response(response.content)
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            raise
    
    def _clean_sql_response(self, response: str) -> str:
        """
        Clean the LLM response to extract only the SQL query.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Cleaned SQL query
        """
        sql_query = response.strip()
        
        # Remove markdown formatting if present
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        elif sql_query.startswith("```"):
            sql_query = sql_query[3:]
            
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        # Remove common prefixes that some LLMs add
        prefixes_to_remove = [
            "Query:",
            "SQL:",
            "Answer:",
            "Result:",
            "Here's the SQL query:",
            "The SQL query is:",
        ]
        
        for prefix in prefixes_to_remove:
            if sql_query.lower().startswith(prefix.lower()):
                sql_query = sql_query[len(prefix):].strip()
        
        # Remove trailing semicolons and whitespace
        sql_query = sql_query.rstrip(';').strip()
        
        return sql_query
    
    async def refine_query(self, 
                          original_query: str, 
                          feedback: str, 
                          schema_info: Dict[str, Any]) -> str:
        """
        Refine an existing SQL query based on feedback.
        
        Args:
            original_query: Original SQL query
            feedback: Feedback or correction instructions
            schema_info: Database schema information
            
        Returns:
            Refined SQL query
        """
        refinement_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SQL optimizer. Refine the given SQL query 
            based on the provided feedback while maintaining the original intent.
            
            Database Schema: {schema_info}"""),
            ("human", """Original Query: {original_query}
            
            Feedback: {feedback}
            
            Please provide the refined SQL query:""")
        ])
        
        try:
            formatted_prompt = refinement_prompt.format_messages(
                schema_info=schema_info,
                original_query=original_query,
                feedback=feedback
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            refined_query = self._clean_sql_response(response.content)
            
            return refined_query
            
        except Exception as e:
            logger.error(f"Query refinement failed: {e}")
            return original_query
