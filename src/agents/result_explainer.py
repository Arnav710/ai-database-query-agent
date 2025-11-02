"""
Result Explainer Agent

This agent provides human-readable explanations of SQL queries
and their results to help users understand what the query does.
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.config import Settings
import logging

logger = logging.getLogger(__name__)


class ResultExplainerAgent:
    """
    Agent responsible for generating human-readable explanations
    of SQL queries and their results.
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
        """Set up prompt templates for explanation generation."""
        
        self.explanation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a SQL expert who explains database queries in simple, 
            human-readable terms. Your explanations should be clear, concise, and accessible 
            to users with varying levels of SQL knowledge.
            
            Guidelines:
            1. Explain what the query does in business terms
            2. Break down complex operations step by step
            3. Highlight important conditions and filters
            4. Explain joins and relationships between tables
            5. Provide context about the results
            6. Use plain English, avoid technical jargon where possible
            
            Database Schema Context: {schema_info}"""),
            ("human", """Original Question: {original_question}
            
            SQL Query: {sql_query}
            
            Query Results Summary: {results_summary}
            
            Please provide a clear explanation of what this query does and what the results mean:""")
        ])
        
        self.results_summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """Summarize the key insights from these database query results. 
            Focus on patterns, trends, and notable findings that would be meaningful to a business user."""),
            ("human", "Query Results: {results}\n\nPlease summarize the key insights:")
        ])
    
    async def explain(self, 
                     original_question: str, 
                     sql_query: str, 
                     results: List[Dict[str, Any]], 
                     schema_info: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of the SQL query and results.
        
        Args:
            original_question: Original natural language question
            sql_query: Generated SQL query
            results: Query execution results
            schema_info: Database schema information
            
        Returns:
            Human-readable explanation string
        """
        try:
            logger.info("Generating query explanation")
            
            # Create results summary
            results_summary = self._create_results_summary(results)
            
            # Generate explanation
            formatted_prompt = self.explanation_prompt.format_messages(
                schema_info=self._format_schema_for_explanation(schema_info),
                original_question=original_question,
                sql_query=sql_query,
                results_summary=results_summary
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            explanation = response.content.strip()
            
            logger.info("Generated query explanation successfully")
            return explanation
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return f"Unable to generate explanation: {e}"
    
    def _create_results_summary(self, results: List[Dict[str, Any]]) -> str:
        """Create a summary of query results for explanation context."""
        if not results:
            return "No results returned"
        
        summary_parts = []
        
        # Basic statistics
        row_count = len(results)
        summary_parts.append(f"Returned {row_count} row{'s' if row_count != 1 else ''}")
        
        if results:
            # Column information
            columns = list(results[0].keys())
            summary_parts.append(f"Columns: {', '.join(columns)}")
            
            # Sample data for first few rows
            if row_count <= 5:
                summary_parts.append(f"Sample data: {results[:3]}")
            else:
                summary_parts.append(f"Sample data (first 3 rows): {results[:3]}")
        
        return ". ".join(summary_parts)
    
    def _format_schema_for_explanation(self, schema_info: Dict[str, Any]) -> str:
        """Format schema information for use in explanations."""
        if not schema_info:
            return "Schema information not available"
        
        formatted_parts = []
        
        # Format table information
        if "tables" in schema_info:
            table_names = [table.get("name", "unknown") for table in schema_info["tables"]]
            formatted_parts.append(f"Available tables: {', '.join(table_names)}")
        
        # Format relationship information
        if "relationships" in schema_info and schema_info["relationships"]:
            formatted_parts.append("Table relationships exist between tables")
        
        return ". ".join(formatted_parts) if formatted_parts else "Basic schema information available"
    
    async def explain_query_only(self, sql_query: str, schema_info: Dict[str, Any]) -> str:
        """
        Explain just the SQL query without results.
        
        Args:
            sql_query: SQL query to explain
            schema_info: Database schema information
            
        Returns:
            Explanation of what the query does
        """
        query_explanation_prompt = ChatPromptTemplate.from_messages([
            ("system", """Explain this SQL query in simple, human-readable terms. 
            Focus on what data it retrieves and how it processes that data.
            
            Database Schema: {schema_info}"""),
            ("human", "SQL Query: {sql_query}\n\nPlease explain what this query does:")
        ])
        
        try:
            formatted_prompt = query_explanation_prompt.format_messages(
                schema_info=self._format_schema_for_explanation(schema_info),
                sql_query=sql_query
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Query explanation failed: {e}")
            return f"Unable to explain query: {e}"
    
    async def summarize_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate insights summary from query results.
        
        Args:
            results: Query execution results
            
        Returns:
            Summary of key insights from the results
        """
        if not results:
            return "No results to summarize"
        
        try:
            # Limit results for summarization to avoid token limits
            sample_results = results[:100] if len(results) > 100 else results
            
            formatted_prompt = self.results_summary_prompt.format_messages(
                results=sample_results
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            summary = response.content.strip()
            
            # Add context about data size if results were truncated
            if len(results) > 100:
                summary += f"\n\nNote: Summary based on first 100 rows of {len(results)} total results."
            
            return summary
            
        except Exception as e:
            logger.error(f"Results summarization failed: {e}")
            return f"Unable to summarize results: {e}"
    
    def create_query_breakdown(self, sql_query: str) -> Dict[str, Any]:
        """
        Create a structured breakdown of SQL query components.
        
        Args:
            sql_query: SQL query to analyze
            
        Returns:
            Dictionary with query component breakdown
        """
        import re
        
        breakdown = {
            "query_type": "Unknown",
            "tables": [],
            "columns": [],
            "conditions": [],
            "joins": [],
            "aggregations": [],
            "sorting": []
        }
        
        # Determine query type
        if re.search(r'^\s*SELECT', sql_query, re.IGNORECASE):
            breakdown["query_type"] = "SELECT (Data Retrieval)"
        elif re.search(r'^\s*INSERT', sql_query, re.IGNORECASE):
            breakdown["query_type"] = "INSERT (Data Addition)"
        elif re.search(r'^\s*UPDATE', sql_query, re.IGNORECASE):
            breakdown["query_type"] = "UPDATE (Data Modification)"
        elif re.search(r'^\s*DELETE', sql_query, re.IGNORECASE):
            breakdown["query_type"] = "DELETE (Data Removal)"
        
        # Extract tables
        table_matches = re.findall(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
        breakdown["tables"].extend(table_matches)
        
        join_matches = re.findall(r'JOIN\s+(\w+)', sql_query, re.IGNORECASE)
        breakdown["tables"].extend(join_matches)
        
        # Extract conditions
        where_matches = re.findall(r'WHERE\s+(.+?)(?:\s+GROUP|\s+ORDER|\s+LIMIT|$)', sql_query, re.IGNORECASE)
        if where_matches:
            breakdown["conditions"] = [condition.strip() for condition in where_matches]
        
        # Extract joins
        join_conditions = re.findall(r'JOIN\s+\w+\s+ON\s+([^WHERE^GROUP^ORDER^LIMIT]+)', sql_query, re.IGNORECASE)
        breakdown["joins"] = [join.strip() for join in join_conditions]
        
        # Extract aggregations
        agg_matches = re.findall(r'\b(COUNT|SUM|AVG|MIN|MAX)\s*\([^)]+\)', sql_query, re.IGNORECASE)
        breakdown["aggregations"] = agg_matches
        
        # Extract sorting
        order_matches = re.findall(r'ORDER\s+BY\s+([^LIMIT]+)', sql_query, re.IGNORECASE)
        if order_matches:
            breakdown["sorting"] = [order.strip() for order in order_matches]
        
        return breakdown
