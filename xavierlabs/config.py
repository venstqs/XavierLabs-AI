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

    # API Keys & Endpoints (Use ANY provider you want, or 100% local Ollama/OpenCode)
    OPENROUTER_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # Custom / Local OpenAI-compatible API base (e.g. LM Studio, vLLM, OpenCode, LocalAI)
    OPENAI_API_BASE: Optional[str] = None

    # Universal model override (if set, applies to all agents unless overridden per role)
    DEFAULT_MODEL: Optional[str] = None

    # Model Routing (via LiteLLM syntax, e.g.:
    #   'openrouter/deepseek/deepseek-r1',
    #   'deepseek/deepseek-chat',
    #   'ollama/deepseek-r1',
    #   'groq/llama-3.3-70b-versatile',
    #   'gemini/gemini-2.5-flash',
    #   'gpt-4o-mini',
    #   'openai/custom-model')
    IDEATOR_MODEL: str = "auto"
    REVIEWER_MODEL: str = "auto"
    CODER_MODEL: str = "auto"
    SYNTHESIZER_MODEL: str = "auto"

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
