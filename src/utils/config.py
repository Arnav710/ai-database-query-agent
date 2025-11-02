"""
Configuration management for the AI Database Query Agent.

This module handles application settings, environment variables,
and configuration validation using Pydantic Settings.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseSettings, Field, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # LLM Provider Configuration
    llm_provider: Literal["openai", "ollama", "anthropic"] = Field("ollama", env="LLM_PROVIDER")
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    langsmith_api_key: Optional[str] = Field(None, env="LANGSMITH_API_KEY")
    
    # Ollama Configuration
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field("codellama:7b", env="OLLAMA_MODEL")
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(True, env="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field("ai-database-query-agent", env="LANGCHAIN_PROJECT")
    langchain_endpoint: str = Field("https://api.smith.langchain.com", env="LANGCHAIN_ENDPOINT")
    
    # Database Configuration
    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_db: str = Field("", env="POSTGRES_DB")
    postgres_user: str = Field("", env="POSTGRES_USER")
    postgres_password: str = Field("", env="POSTGRES_PASSWORD")
    
    mysql_host: str = Field("localhost", env="MYSQL_HOST")
    mysql_port: int = Field(3306, env="MYSQL_PORT")
    mysql_db: str = Field("", env="MYSQL_DB")
    mysql_user: str = Field("", env="MYSQL_USER")
    mysql_password: str = Field("", env="MYSQL_PASSWORD")
    
    mongodb_uri: str = Field("mongodb://localhost:27017/", env="MONGODB_URI")
    sqlite_path: str = Field("./data/database.db", env="SQLITE_PATH")
    
    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(False, env="DEBUG")
    max_query_timeout: int = Field(30, env="MAX_QUERY_TIMEOUT")
    max_results_limit: int = Field(1000, env="MAX_RESULTS_LIMIT")
    
    # Security Configuration
    secret_key: str = Field("your_secret_key_here", env="SECRET_KEY")
    allowed_hosts: List[str] = Field(["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # Rate Limiting
    rate_limit_queries_per_minute: int = Field(60, env="RATE_LIMIT_QUERIES_PER_MINUTE")
    rate_limit_queries_per_hour: int = Field(1000, env="RATE_LIMIT_QUERIES_PER_HOUR")
    
    # Query Safety
    allow_write_operations: bool = Field(False, env="ALLOW_WRITE_OPERATIONS")
    allow_schema_changes: bool = Field(False, env="ALLOW_SCHEMA_CHANGES")
    enable_query_cost_estimation: bool = Field(True, env="ENABLE_QUERY_COST_ESTIMATION")
    
    # Model Configuration
    default_llm_model: str = Field("gpt-4", env="DEFAULT_LLM_MODEL")
    temperature: float = Field(0.1, env="TEMPERATURE")
    max_tokens: int = Field(2000, env="MAX_TOKENS")
    
    @validator("llm_provider")
    def validate_llm_provider(cls, v):
        if v not in ["openai", "ollama", "anthropic"]:
            raise ValueError("LLM provider must be one of: openai, ollama, anthropic")
        return v
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v, values):
        if values.get("llm_provider") == "openai" and not v:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @property
    def postgres_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        if not all([self.postgres_user, self.postgres_password, self.postgres_db]):
            return ""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def mysql_connection_string(self) -> str:
        """Generate MySQL connection string."""
        if not all([self.mysql_user, self.mysql_password, self.mysql_db]):
            return ""
        return f"mysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


def create_data_directory():
    """Create data directory if it doesn't exist."""
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    return data_dir
