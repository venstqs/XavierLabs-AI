import os
from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # Model Routing (via LiteLLM syntax, e.g., 'gemini/gemini-2.5-flash', 'ollama/deepseek-r1', 'gpt-4o-mini')
    IDEATOR_MODEL: str = "gemini/gemini-2.5-flash"
    REVIEWER_MODEL: str = "gemini/gemini-2.5-flash"
    CODER_MODEL: str = "gemini/gemini-2.5-flash"
    SYNTHESIZER_MODEL: str = "gemini/gemini-2.5-flash"

    # Execution Sandbox Settings
    SANDBOX_MODE: Literal["auto", "docker", "local"] = "auto"
    DOCKER_IMAGE: str = "python:3.11-slim"
    EXECUTION_TIMEOUT: int = 180  # seconds
    EXPERIMENT_TIMEOUT_SECONDS: int = 180
    MAX_DEBUG_RETRIES: int = 3

    # Storage & Persistence
    DB_PATH: str = "xavierlabs.db"
    WORKSPACE_DIR: Path = Path("experiments")

    # Local Ollama endpoint if used
    OLLAMA_API_BASE: str = "http://localhost:11434"


settings = Settings()

# Ensure workspace directory exists
settings.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
