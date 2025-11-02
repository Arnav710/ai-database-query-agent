"""
Safety Validator Agent

This agent validates SQL queries for safety, security,
and compliance before execution.
"""

from typing import List, Dict, Any
import re
from src.models.query import SafetyValidationResult
from src.utils.config import Settings
import logging

logger = logging.getLogger(__name__)


class SafetyValidatorAgent:
    """
    Agent responsible for validating SQL queries for safety,
    security vulnerabilities, and compliance with organizational policies.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._setup_safety_rules()
    
    def _setup_safety_rules(self):
        """Set up safety validation rules."""
        
        # Dangerous operations that should be blocked
        self.dangerous_operations = [
            r'\bDROP\s+TABLE\b',
            r'\bDROP\s+DATABASE\b',
            r'\bTRUNCATE\b',
            r'\bALTER\s+TABLE\b',
            r'\bCREATE\s+TABLE\b',
            r'\bDELETE\s+FROM\b(?!\s+\w+\s+WHERE)',  # DELETE without WHERE
            r'\bUPDATE\b(?!.*WHERE)',  # UPDATE without WHERE
        ]
        
        # Write operations (may be restricted)
        self.write_operations = [
            r'\bINSERT\b',
            r'\bUPDATE\b',
            r'\bDELETE\b',
            r'\bMERGE\b',
            r'\bREPLACE\b'
        ]
        
        # Schema modification operations
        self.schema_operations = [
            r'\bCREATE\b',
            r'\bALTER\b',
            r'\bDROP\b',
            r'\bRENAME\b'
        ]
        
        # Potentially dangerous functions
        self.dangerous_functions = [
            r'\bEXEC\b',
            r'\bEVAL\b',
            r'\bxp_cmdshell\b',
            r'\bsp_executesql\b'
        ]
    
    async def validate(self, sql_query: str, connection_name: str) -> SafetyValidationResult:
        """
        Validate SQL query for safety and security issues.
        
        Args:
            sql_query: SQL query to validate
            connection_name: Database connection name
            
        Returns:
            SafetyValidationResult with validation outcome
        """
        try:
            logger.info(f"Validating query safety for connection: {connection_name}")
            
            issues = []
            recommendations = []
            risk_level = "low"
            
            # Normalize query for analysis
            normalized_query = sql_query.upper().strip()
            
            # Check for dangerous operations
            for pattern in self.dangerous_operations:
                if re.search(pattern, normalized_query, re.IGNORECASE):
                    issues.append(f"Dangerous operation detected: {pattern}")
                    risk_level = "high"
            
            # Check write operations if not allowed
            if not self.settings.allow_write_operations:
                for pattern in self.write_operations:
                    if re.search(pattern, normalized_query, re.IGNORECASE):
                        issues.append(f"Write operation not allowed: {pattern}")
                        risk_level = "medium"
            
            # Check schema operations if not allowed
            if not self.settings.allow_schema_changes:
                for pattern in self.schema_operations:
                    if re.search(pattern, normalized_query, re.IGNORECASE):
                        issues.append(f"Schema modification not allowed: {pattern}")
                        risk_level = "high"
            
            # Check for dangerous functions
            for pattern in self.dangerous_functions:
                if re.search(pattern, normalized_query, re.IGNORECASE):
                    issues.append(f"Dangerous function detected: {pattern}")
                    risk_level = "high"
            
            # Check for SQL injection patterns
            injection_issues = self._check_sql_injection(sql_query)
            if injection_issues:
                issues.extend(injection_issues)
                risk_level = "high"
            
            # Generate recommendations
            if issues:
                recommendations = self._generate_recommendations(issues)
            
            is_safe = len(issues) == 0 or (risk_level == "low" and self.settings.allow_write_operations)
            
            return SafetyValidationResult(
                is_safe=is_safe,
                issues=issues,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Safety validation failed: {e}")
            return SafetyValidationResult(
                is_safe=False,
                issues=[f"Validation error: {e}"],
                risk_level="high",
                recommendations=["Please review the query manually"]
            )
    
    def _check_sql_injection(self, sql_query: str) -> List[str]:
        """Check for potential SQL injection patterns."""
        issues = []
        
        # Common SQL injection patterns
        injection_patterns = [
            r"';.*--",  # Comment injection
            r"UNION\s+SELECT",  # Union injection
            r"1=1",  # Always true condition
            r"OR\s+1=1",  # OR injection
            r"DROP\s+TABLE",  # Drop table injection
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                issues.append(f"Potential SQL injection pattern: {pattern}")
        
        return issues
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate safety recommendations based on identified issues."""
        recommendations = []
        
        if any("injection" in issue.lower() for issue in issues):
            recommendations.append("Use parameterized queries to prevent SQL injection")
        
        if any("write operation" in issue.lower() for issue in issues):
            recommendations.append("Consider using read-only database connections for analytics")
        
        if any("dangerous operation" in issue.lower() for issue in issues):
            recommendations.append("Review and approve destructive operations manually")
        
        if any("schema modification" in issue.lower() for issue in issues):
            recommendations.append("Schema changes should go through proper change management")
        
        return recommendations
    
    def estimate_query_cost(self, sql_query: str) -> Dict[str, Any]:
        """
        Estimate the computational cost of a query.
        
        Args:
            sql_query: SQL query to analyze
            
        Returns:
            Dict with cost estimation information
        """
        # Simple heuristic-based cost estimation
        cost_factors = {
            "table_scans": len(re.findall(r'\bFROM\s+\w+', sql_query, re.IGNORECASE)),
            "joins": len(re.findall(r'\bJOIN\b', sql_query, re.IGNORECASE)),
            "subqueries": len(re.findall(r'\bSELECT\b', sql_query, re.IGNORECASE)) - 1,
            "aggregations": len(re.findall(r'\b(COUNT|SUM|AVG|MIN|MAX|GROUP BY)\b', sql_query, re.IGNORECASE)),
            "sorts": len(re.findall(r'\bORDER BY\b', sql_query, re.IGNORECASE))
        }
        
        # Calculate relative cost score
        cost_score = (
            cost_factors["table_scans"] * 1 +
            cost_factors["joins"] * 2 +
            cost_factors["subqueries"] * 3 +
            cost_factors["aggregations"] * 2 +
            cost_factors["sorts"] * 2
        )
        
        if cost_score <= 5:
            cost_level = "low"
        elif cost_score <= 15:
            cost_level = "medium"
        else:
            cost_level = "high"
        
        return {
            "cost_score": cost_score,
            "cost_level": cost_level,
            "factors": cost_factors,
            "recommendations": self._get_performance_recommendations(cost_factors)
        }
    
    def _get_performance_recommendations(self, cost_factors: Dict[str, int]) -> List[str]:
        """Generate performance recommendations based on cost factors."""
        recommendations = []
        
        if cost_factors["joins"] > 3:
            recommendations.append("Consider reducing the number of joins or using subqueries")
        
        if cost_factors["subqueries"] > 2:
            recommendations.append("Review subqueries for optimization opportunities")
        
        if cost_factors["sorts"] > 1:
            recommendations.append("Multiple ORDER BY clauses may impact performance")
        
        return recommendations
