"""
Query Optimizer Agent

This agent analyzes SQL queries for performance optimization
opportunities and suggests improvements.
"""

from typing import Dict, Any, List
from src.models.query import QueryOptimizationResult
from src.utils.config import Settings
import re
import logging

logger = logging.getLogger(__name__)


class QueryOptimizerAgent:
    """
    Agent responsible for analyzing and optimizing SQL queries
    for better performance and efficiency.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def optimize(self, sql_query: str, schema_info: Dict[str, Any]) -> QueryOptimizationResult:
        """
        Analyze and optimize SQL query for better performance.
        
        Args:
            sql_query: Original SQL query
            schema_info: Database schema information
            
        Returns:
            QueryOptimizationResult with optimized query and suggestions
        """
        try:
            logger.info("Analyzing query for optimization opportunities")
            
            suggestions = []
            optimized_query = sql_query
            
            # Analyze query patterns and suggest optimizations
            suggestions.extend(self._analyze_joins(sql_query))
            suggestions.extend(self._analyze_where_clauses(sql_query))
            suggestions.extend(self._analyze_select_clauses(sql_query))
            suggestions.extend(self._analyze_subqueries(sql_query))
            suggestions.extend(self._analyze_aggregations(sql_query))
            
            # Apply optimizations where possible
            optimized_query = self._apply_optimizations(sql_query, suggestions)
            
            # Estimate performance improvement
            performance_improvement = self._estimate_improvement(sql_query, optimized_query)
            
            return QueryOptimizationResult(
                optimized_query=optimized_query,
                suggestions=suggestions,
                estimated_cost=None,  # Would integrate with database query planner
                performance_improvement=performance_improvement
            )
            
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            return QueryOptimizationResult(
                optimized_query=sql_query,
                suggestions=[f"Optimization error: {e}"],
                estimated_cost=None,
                performance_improvement=None
            )
    
    def _analyze_joins(self, sql_query: str) -> List[str]:
        """Analyze JOIN operations for optimization opportunities."""
        suggestions = []
        
        # Check for missing JOIN conditions
        join_count = len(re.findall(r'\bJOIN\b', sql_query, re.IGNORECASE))
        on_count = len(re.findall(r'\bON\b', sql_query, re.IGNORECASE))
        
        if join_count > on_count:
            suggestions.append("Some JOINs may be missing ON conditions - consider adding explicit join conditions")
        
        # Check for Cartesian products
        if re.search(r'FROM\s+\w+\s*,\s*\w+', sql_query, re.IGNORECASE):
            suggestions.append("Consider using explicit JOIN syntax instead of comma-separated tables")
        
        # Suggest using appropriate JOIN types
        if re.search(r'\bLEFT\s+JOIN\b', sql_query, re.IGNORECASE):
            suggestions.append("Review LEFT JOINs - consider if INNER JOIN is sufficient")
        
        return suggestions
    
    def _analyze_where_clauses(self, sql_query: str) -> List[str]:
        """Analyze WHERE clauses for optimization opportunities."""
        suggestions = []
        
        # Check for functions in WHERE clauses
        if re.search(r'WHERE.*\w+\([^)]*\w+\.[^)]*\)', sql_query, re.IGNORECASE):
            suggestions.append("Functions in WHERE clauses may prevent index usage - consider alternatives")
        
        # Check for LIKE with leading wildcards
        if re.search(r"LIKE\s+['\"]%", sql_query, re.IGNORECASE):
            suggestions.append("LIKE patterns starting with % cannot use indexes effectively")
        
        # Check for OR conditions
        if re.search(r'\bOR\b', sql_query, re.IGNORECASE):
            suggestions.append("OR conditions may prevent index usage - consider UNION or separate queries")
        
        # Check for inequalities
        inequality_count = len(re.findall(r'[<>!]', sql_query))
        if inequality_count > 2:
            suggestions.append("Multiple inequality conditions may limit index effectiveness")
        
        return suggestions
    
    def _analyze_select_clauses(self, sql_query: str) -> List[str]:
        """Analyze SELECT clauses for optimization opportunities."""
        suggestions = []
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', sql_query, re.IGNORECASE):
            suggestions.append("SELECT * fetches all columns - specify only needed columns for better performance")
        
        # Check for unnecessary DISTINCT
        if re.search(r'\bDISTINCT\b', sql_query, re.IGNORECASE):
            suggestions.append("Review if DISTINCT is necessary - it adds sorting overhead")
        
        # Check for complex expressions in SELECT
        if re.search(r'SELECT.*CASE\s+WHEN', sql_query, re.IGNORECASE):
            suggestions.append("Complex CASE expressions in SELECT may impact performance")
        
        return suggestions
    
    def _analyze_subqueries(self, sql_query: str) -> List[str]:
        """Analyze subqueries for optimization opportunities."""
        suggestions = []
        
        # Count subqueries
        subquery_count = len(re.findall(r'\bSELECT\b', sql_query, re.IGNORECASE)) - 1
        
        if subquery_count > 2:
            suggestions.append("Multiple subqueries detected - consider JOINs or CTEs for better performance")
        
        # Check for correlated subqueries
        if re.search(r'WHERE.*IN\s*\(\s*SELECT', sql_query, re.IGNORECASE):
            suggestions.append("EXISTS may perform better than IN with subqueries")
        
        # Check for NOT IN subqueries
        if re.search(r'NOT\s+IN\s*\(\s*SELECT', sql_query, re.IGNORECASE):
            suggestions.append("NOT EXISTS typically performs better than NOT IN with subqueries")
        
        return suggestions
    
    def _analyze_aggregations(self, sql_query: str) -> List[str]:
        """Analyze aggregation functions for optimization opportunities."""
        suggestions = []
        
        # Check for HAVING without GROUP BY
        if re.search(r'\bHAVING\b', sql_query, re.IGNORECASE) and not re.search(r'\bGROUP\s+BY\b', sql_query, re.IGNORECASE):
            suggestions.append("HAVING without GROUP BY may be inefficient - consider WHERE clause")
        
        # Check for aggregations with DISTINCT
        if re.search(r'(COUNT|SUM|AVG)\s*\(\s*DISTINCT', sql_query, re.IGNORECASE):
            suggestions.append("Aggregations with DISTINCT require additional processing")
        
        return suggestions
    
    def _apply_optimizations(self, sql_query: str, suggestions: List[str]) -> str:
        """Apply automatic optimizations where safe to do so."""
        optimized_query = sql_query
        
        # Apply safe optimizations
        # Note: In a real implementation, this would be more sophisticated
        
        # Convert comma joins to explicit JOINs (if safe)
        # This is a simplified example - real implementation would need careful parsing
        
        return optimized_query
    
    def _estimate_improvement(self, original_query: str, optimized_query: str) -> str:
        """Estimate performance improvement between original and optimized queries."""
        
        if original_query == optimized_query:
            return "No optimizations applied"
        
        # Simple heuristic-based estimation
        original_complexity = self._calculate_complexity(original_query)
        optimized_complexity = self._calculate_complexity(optimized_query)
        
        if optimized_complexity < original_complexity:
            improvement_percent = ((original_complexity - optimized_complexity) / original_complexity) * 100
            return f"Estimated {improvement_percent:.1f}% performance improvement"
        else:
            return "Performance impact analysis needed"
    
    def _calculate_complexity(self, sql_query: str) -> int:
        """Calculate a simple complexity score for a SQL query."""
        complexity = 0
        
        # Add complexity for various operations
        complexity += len(re.findall(r'\bJOIN\b', sql_query, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'\bSELECT\b', sql_query, re.IGNORECASE)) * 1
        complexity += len(re.findall(r'\bWHERE\b', sql_query, re.IGNORECASE)) * 1
        complexity += len(re.findall(r'\bGROUP BY\b', sql_query, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'\bORDER BY\b', sql_query, re.IGNORECASE)) * 2
        complexity += len(re.findall(r'\bHAVING\b', sql_query, re.IGNORECASE)) * 2
        complexity += sql_query.count('*') * 1
        
        return complexity
    
    def suggest_indexes(self, sql_query: str, schema_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest database indexes based on query patterns.
        
        Args:
            sql_query: SQL query to analyze
            schema_info: Database schema information
            
        Returns:
            List of index suggestions
        """
        suggestions = []
        
        # Extract columns used in WHERE clauses
        where_columns = re.findall(r'WHERE.*?(\w+)\s*[=<>]', sql_query, re.IGNORECASE)
        
        for column in where_columns:
            suggestions.append({
                "type": "single_column_index",
                "column": column,
                "reason": "Column used in WHERE clause",
                "priority": "high"
            })
        
        # Extract columns used in JOIN conditions
        join_columns = re.findall(r'ON\s+(\w+\.\w+)\s*=\s*(\w+\.\w+)', sql_query, re.IGNORECASE)
        
        for join_pair in join_columns:
            for column in join_pair:
                suggestions.append({
                    "type": "join_index",
                    "column": column,
                    "reason": "Column used in JOIN condition",
                    "priority": "medium"
                })
        
        return suggestions
