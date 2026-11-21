import os
from pathlib import Path
from typing import Any, Literal, Optional
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            str(Path.home() / ".xavierlabs" / ".env"),
            str(Path.home() / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys & Endpoints (Use ANY provider you want, or 100% local Ollama/OpenCode)
    OPENROUTER_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    @field_validator(
        "OPENROUTER_API_KEY",
        "DEEPSEEK_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GROQ_API_KEY",
        "TAVILY_API_KEY",
        "OPENAI_API_BASE",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def clean_key_string(cls, v: Any) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip("'\" \t\r\n")
            return cleaned if cleaned else None
        return v

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
    # Default image is built automatically on first use (python:3.11-slim + numpy/scipy/matplotlib/...)
    DOCKER_IMAGE: str = "xavierlabs-sandbox:latest"
    DOCKER_NETWORK: str = "none"  # "none" = no network access for generated code; use "bridge" to allow it
    DOCKER_MEM_LIMIT: str = "2g"
    DOCKER_CPUS: float = 2.0
    # Seconds per sandboxed script run. EXPERIMENT_TIMEOUT_SECONDS is accepted as a legacy alias.
    EXECUTION_TIMEOUT: int = Field(
        default=180,
        validation_alias=AliasChoices("EXECUTION_TIMEOUT", "EXPERIMENT_TIMEOUT_SECONDS"),
    )
    MAX_DEBUG_RETRIES: int = 3

    # Hypothesis peer review: how many times the Ideator may revise a rejected hypothesis,
    # and whether to run the experiment anyway if the final revision is still rejected.
    MAX_REFINEMENT_ROUNDS: int = 2
    PROCEED_IF_REJECTED: bool = False

    # Storage & Persistence
    DB_PATH: str = "xavierlabs.db"
    WORKSPACE_DIR: Path = Path("experiments")

    # Local Ollama endpoint if used
    OLLAMA_API_BASE: str = "http://localhost:11434"


settings = Settings()

# Ensure workspace directory exists
settings.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
