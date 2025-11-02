"""
Database Query Workflow using LangGraph

This module defines the multi-agent workflow for processing database queries
using LangGraph's state management and agent orchestration capabilities.
"""

from typing import Dict, Any, List, Optional
from langgraph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from src.models.query import QueryRequest, QueryResponse
from src.agents.schema_analyzer import SchemaAnalyzerAgent
from src.agents.query_generator import QueryGeneratorAgent
from src.agents.safety_validator import SafetyValidatorAgent
from src.agents.query_optimizer import QueryOptimizerAgent
from src.agents.result_explainer import ResultExplainerAgent
from src.utils.config import Settings
import logging

logger = logging.getLogger(__name__)


class DatabaseQueryState:
    """State object for the database query workflow."""
    
    def __init__(self):
        self.request: Optional[QueryRequest] = None
        self.schema_info: Dict[str, Any] = {}
        self.generated_sql: str = ""
        self.safety_validated: bool = False
        self.optimized_sql: str = ""
        self.query_results: List[Dict[str, Any]] = []
        self.explanation: str = ""
        self.errors: List[str] = []
        self.metadata: Dict[str, Any] = {}


class DatabaseQueryWorkflow:
    """
    LangGraph workflow for processing database queries through multiple agents.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.graph = self._build_workflow()
        
        # Initialize agents
        self.schema_analyzer = SchemaAnalyzerAgent(settings)
        self.query_generator = QueryGeneratorAgent(settings)
        self.safety_validator = SafetyValidatorAgent(settings)
        self.query_optimizer = QueryOptimizerAgent(settings)
        self.result_explainer = ResultExplainerAgent(settings)
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for query processing."""
        
        workflow = StateGraph(DatabaseQueryState)
        
        # Add nodes for each agent
        workflow.add_node("analyze_schema", self._analyze_schema_node)
        workflow.add_node("generate_query", self._generate_query_node)
        workflow.add_node("validate_safety", self._validate_safety_node)
        workflow.add_node("optimize_query", self._optimize_query_node)
        workflow.add_node("execute_query", self._execute_query_node)
        workflow.add_node("explain_results", self._explain_results_node)
        
        # Define the workflow edges
        workflow.add_edge(START, "analyze_schema")
        workflow.add_edge("analyze_schema", "generate_query")
        workflow.add_edge("generate_query", "validate_safety")
        
        # Conditional edge based on safety validation
        workflow.add_conditional_edges(
            "validate_safety",
            self._should_proceed_after_validation,
            {
                "optimize": "optimize_query",
                "reject": END
            }
        )
        
        workflow.add_edge("optimize_query", "execute_query")
        workflow.add_edge("execute_query", "explain_results")
        workflow.add_edge("explain_results", END)
        
        return workflow.compile()
    
    async def _analyze_schema_node(self, state: DatabaseQueryState) -> DatabaseQueryState:
        """Node for schema analysis."""
        try:
            logger.info("Analyzing database schema")
            state.schema_info = await self.schema_analyzer.analyze(
                state.request.connection_name
            )
        except Exception as e:
            logger.error(f"Schema analysis failed: {e}")
            state.errors.append(f"Schema analysis error: {e}")
        
        return state
    
    async def _generate_query_node(self, state: DatabaseQueryState) -> DatabaseQueryState:
        """Node for SQL query generation."""
        try:
            logger.info("Generating SQL query")
            state.generated_sql = await self.query_generator.generate(
                state.request.query,
                state.schema_info,
                state.request.context
            )
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            state.errors.append(f"Query generation error: {e}")
        
        return state
    
    async def _validate_safety_node(self, state: DatabaseQueryState) -> DatabaseQueryState:
        """Node for safety validation."""
        try:
            logger.info("Validating query safety")
            validation_result = await self.safety_validator.validate(
                state.generated_sql,
                state.request.connection_name
            )
            state.safety_validated = validation_result.is_safe
            if not validation_result.is_safe:
                state.errors.extend(validation_result.issues)
        except Exception as e:
            logger.error(f"Safety validation failed: {e}")
            state.errors.append(f"Safety validation error: {e}")
            state.safety_validated = False
        
        return state
    
    async def _optimize_query_node(self, state: DatabaseQueryState) -> DatabaseQueryState:
        """Node for query optimization."""
        try:
            logger.info("Optimizing SQL query")
            optimization_result = await self.query_optimizer.optimize(
                state.generated_sql,
                state.schema_info
            )
            state.optimized_sql = optimization_result.optimized_query
            state.metadata["optimization_suggestions"] = optimization_result.suggestions
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            state.errors.append(f"Query optimization error: {e}")
            state.optimized_sql = state.generated_sql
        
        return state
    
    async def _execute_query_node(self, state: DatabaseQueryState) -> DatabaseQueryState:
        """Node for query execution."""
        try:
            logger.info("Executing SQL query")
            # This would integrate with the database manager
            # For now, we'll use a placeholder
            state.query_results = []  # Placeholder for actual execution
            state.metadata["execution_time"] = 0.0  # Placeholder
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            state.errors.append(f"Query execution error: {e}")
        
        return state
    
    async def _explain_results_node(self, state: DatabaseQueryState) -> DatabaseQueryState:
        """Node for result explanation."""
        try:
            logger.info("Generating query explanation")
            state.explanation = await self.result_explainer.explain(
                state.request.query,
                state.optimized_sql or state.generated_sql,
                state.query_results,
                state.schema_info
            )
        except Exception as e:
            logger.error(f"Result explanation failed: {e}")
            state.errors.append(f"Result explanation error: {e}")
            state.explanation = "Unable to generate explanation"
        
        return state
    
    def _should_proceed_after_validation(self, state: DatabaseQueryState) -> str:
        """Conditional logic for proceeding after safety validation."""
        return "optimize" if state.safety_validated else "reject"
    
    async def process_query(self, request: QueryRequest) -> QueryResponse:
        """
        Process a query request through the multi-agent workflow.
        
        Args:
            request: The query request to process
            
        Returns:
            QueryResponse: The processed response
        """
        try:
            # Initialize state
            initial_state = DatabaseQueryState()
            initial_state.request = request
            
            # Run the workflow
            result_state = await self.graph.ainvoke(initial_state)
            
            # Build response
            return QueryResponse(
                success=len(result_state.errors) == 0,
                sql_query=result_state.optimized_sql or result_state.generated_sql,
                explanation=result_state.explanation,
                results=result_state.query_results,
                metadata=result_state.metadata,
                error="; ".join(result_state.errors) if result_state.errors else None
            )
            
        except Exception as e:
            logger.error(f"Workflow processing failed: {e}")
            return QueryResponse(
                success=False,
                error=str(e),
                sql_query="",
                explanation="Workflow processing failed",
                results=[]
            )
