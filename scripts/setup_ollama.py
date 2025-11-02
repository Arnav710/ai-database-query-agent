#!/usr/bin/env python3
"""
Ollama Setup Script

This script helps set up Ollama and download recommended models for SQL generation.
"""

import subprocess
import sys
import time
import requests
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaSetup:
    """Helper class for setting up Ollama and models."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.recommended_models = [
            "codellama:7b",     # Best for SQL generation
            "llama2:7b",        # Good general purpose
            "mistral:7b",       # Fast and capable
            "sqlcoder:7b",      # SQL-specific (if available)
        ]
    
    def check_ollama_installed(self) -> bool:
        """Check if Ollama is installed and accessible."""
        try:
            result = subprocess.run(
                ["ollama", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"Ollama is installed: {result.stdout.strip()}")
                return True
            else:
                logger.error("Ollama command failed")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Ollama command timed out")
            return False
        except FileNotFoundError:
            logger.error("Ollama not found. Please install Ollama first.")
            return False
        except Exception as e:
            logger.error(f"Error checking Ollama: {e}")
            return False
    
    def check_ollama_server(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama server is running")
                return True
            else:
                logger.error(f"Ollama server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama server. Is it running?")
            return False
        except Exception as e:
            logger.error(f"Error checking Ollama server: {e}")
            return False
    
    def start_ollama_server(self) -> bool:
        """Start the Ollama server."""
        try:
            logger.info("Starting Ollama server...")
            # Start Ollama in the background
            subprocess.Popen(
                ["ollama", "serve"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check if server is now running
            return self.check_ollama_server()
            
        except Exception as e:
            logger.error(f"Error starting Ollama server: {e}")
            return False
    
    def list_installed_models(self) -> List[str]:
        """List currently installed models."""
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            else:
                logger.error("Failed to list models")
                return []
                
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def download_model(self, model_name: str) -> bool:
        """Download a specific model."""
        try:
            logger.info(f"Downloading model: {model_name}")
            logger.info("This may take several minutes depending on model size...")
            
            result = subprocess.run(
                ["ollama", "pull", model_name], 
                capture_output=True, 
                text=True, 
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded {model_name}")
                return True
            else:
                logger.error(f"Failed to download {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Download of {model_name} timed out")
            return False
        except Exception as e:
            logger.error(f"Error downloading {model_name}: {e}")
            return False
    
    def test_model(self, model_name: str) -> bool:
        """Test if a model is working properly."""
        try:
            logger.info(f"Testing model: {model_name}")
            
            result = subprocess.run([
                "ollama", "run", model_name, 
                "Write a simple SQL query to select all records from a table called 'users'"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and "SELECT" in result.stdout.upper():
                logger.info(f"Model {model_name} is working correctly")
                return True
            else:
                logger.error(f"Model {model_name} test failed")
                return False
                
        except Exception as e:
            logger.error(f"Error testing model {model_name}: {e}")
            return False
    
    def setup_recommended_model(self) -> str:
        """Set up the best available model for SQL generation."""
        installed_models = self.list_installed_models()
        
        # Check if any recommended model is already installed
        for model in self.recommended_models:
            if any(model in installed for installed in installed_models):
                logger.info(f"Found installed model: {model}")
                if self.test_model(model):
                    return model
        
        # Download the first recommended model
        primary_model = self.recommended_models[0]
        logger.info(f"Downloading recommended model: {primary_model}")
        
        if self.download_model(primary_model):
            if self.test_model(primary_model):
                return primary_model
        
        logger.error("Failed to set up any recommended model")
        return ""


def main():
    """Main setup function."""
    print("🚀 Setting up Ollama for AI Database Query Agent")
    print("=" * 50)
    
    setup = OllamaSetup()
    
    # Check if Ollama is installed
    if not setup.check_ollama_installed():
        print("\n❌ Ollama is not installed!")
        print("\nInstallation instructions:")
        print("📦 macOS: brew install ollama")
        print("🐧 Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print("🪟 Windows: Download from https://ollama.ai")
        return False
    
    # Check if server is running, start if needed
    if not setup.check_ollama_server():
        print("\n🔄 Starting Ollama server...")
        if not setup.start_ollama_server():
            print("\n❌ Failed to start Ollama server")
            print("Please run 'ollama serve' manually")
            return False
    
    # Set up recommended model
    print("\n📥 Setting up recommended model for SQL generation...")
    model = setup.setup_recommended_model()
    
    if model:
        print(f"\n✅ Setup complete!")
        print(f"🤖 Recommended model: {model}")
        print(f"\nUpdate your .env file:")
        print(f"LLM_PROVIDER=ollama")
        print(f"OLLAMA_MODEL={model}")
        return True
    else:
        print("\n❌ Setup failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
