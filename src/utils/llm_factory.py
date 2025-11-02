"""
LLM Factory for creating different LLM instances based on configuration.

This module provides a factory pattern to create LLM instances for different providers
like OpenAI, Ollama, or Anthropic based on the application configuration.
"""

from typing import Union
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_anthropic import ChatAnthropic
from src.utils.config import Settings
import logging

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory class for creating LLM instances based on provider configuration."""
    
    @staticmethod
    def create_llm(settings: Settings) -> Union[ChatOpenAI, ChatOllama, ChatAnthropic]:
        """
        Create an LLM instance based on the configured provider.
        
        Args:
            settings: Application settings containing LLM configuration
            
        Returns:
            Configured LLM instance
            
        Raises:
            ValueError: If the provider is not supported
            RuntimeError: If required dependencies are missing
        """
        provider = settings.llm_provider.lower()
        
        try:
            if provider == "openai":
                return LLMFactory._create_openai_llm(settings)
            elif provider == "ollama":
                return LLMFactory._create_ollama_llm(settings)
            elif provider == "anthropic":
                return LLMFactory._create_anthropic_llm(settings)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        except ImportError as e:
            raise RuntimeError(f"Missing dependencies for {provider} provider: {e}")
    
    @staticmethod
    def _create_openai_llm(settings: Settings) -> ChatOpenAI:
        """Create OpenAI LLM instance."""
        logger.info(f"Creating OpenAI LLM with model: {settings.default_llm_model}")
        
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI provider")
        
        return ChatOpenAI(
            model=settings.default_llm_model,
            temperature=settings.temperature,
            api_key=settings.openai_api_key,
            max_tokens=settings.max_tokens
        )
    
    @staticmethod
    def _create_ollama_llm(settings: Settings) -> ChatOllama:
        """Create Ollama LLM instance."""
        logger.info(f"Creating Ollama LLM with model: {settings.ollama_model}")
        logger.info(f"Ollama base URL: {settings.ollama_base_url}")
        
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=settings.temperature,
            num_predict=settings.max_tokens,
            # Additional Ollama-specific parameters for better SQL generation
            stop=[";", "\n\n"],  # Stop at semicolon or double newline
            top_k=10,  # Limit token sampling for more focused responses
            top_p=0.9,  # Nucleus sampling for better quality
        )
    
    @staticmethod
    def _create_anthropic_llm(settings: Settings) -> ChatAnthropic:
        """Create Anthropic LLM instance."""
        logger.info(f"Creating Anthropic LLM with model: claude-3-sonnet-20240229")
        
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key is required for Anthropic provider")
        
        return ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=settings.temperature,
            api_key=settings.anthropic_api_key,
            max_tokens=settings.max_tokens
        )
    
    @staticmethod
    def test_connection(settings: Settings) -> bool:
        """
        Test if the LLM connection is working.
        
        Args:
            settings: Application settings
            
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            llm = LLMFactory.create_llm(settings)
            
            # Simple test prompt
            test_response = llm.invoke("Say 'Hello' if you can hear me.")
            
            if test_response and test_response.content:
                logger.info(f"LLM connection test successful for {settings.llm_provider}")
                return True
            else:
                logger.error(f"LLM connection test failed for {settings.llm_provider}: Empty response")
                return False
                
        except Exception as e:
            logger.error(f"LLM connection test failed for {settings.llm_provider}: {e}")
            return False
