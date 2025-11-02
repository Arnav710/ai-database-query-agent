"""
Query Generator Agent

This agent converts natural language queries into SQL using
the schema context provided by the Schema Analyzer Agent.
"""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.config import Settings
import logging

logger = logging.getLogger(__name__)


class QueryGeneratorAgent:
    """
    Agent responsible for converting natural language queries to SQL
    using database schema context and business logic understanding.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = ChatOpenAI(
            model=settings.default_llm_model,
            temperature=settings.temperature,
            api_key=settings.openai_api_key
        )
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
            6. Return only the SQL query, no explanations
            
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
            
            # Format the prompt with schema and query information
            formatted_prompt = self.generation_prompt.format_messages(
                schema_info=schema_info,
                user_query=user_query,
                context=context or {}
            )
            
            # Generate SQL using LLM
            response = await self.llm.ainvoke(formatted_prompt)
            sql_query = response.content.strip()
            
            # Clean up the response (remove markdown formatting if present)
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            raise
    
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
            refined_query = response.content.strip()
            
            # Clean up formatting
            if refined_query.startswith("```sql"):
                refined_query = refined_query[6:]
            if refined_query.endswith("```"):
                refined_query = refined_query[:-3]
            
            return refined_query.strip()
            
        except Exception as e:
            logger.error(f"Query refinement failed: {e}")
            return original_query
