import os
import json
import re
from typing import Any, Dict, List, Optional
import litellm
from litellm import completion
from xavierlabs.config import settings

# Silence unnecessary litellm telemetry in terminal
litellm.telemetry = False
litellm.drop_params = True


class LLMRouter:
    """
    Hybrid LLM Router using LiteLLM.
    Handles dispatching to frontier models (Gemini, Claude, GPT)
    or local Ollama models based on role configuration.
    """

    def __init__(self):
        self._sync_env_keys()

    def _sync_env_keys(self):
        """Ensures configured API keys are available in environment for LiteLLM."""
        key_mappings = {
            "OPENROUTER_API_KEY": settings.OPENROUTER_API_KEY,
            "DEEPSEEK_API_KEY": settings.DEEPSEEK_API_KEY,
            "GEMINI_API_KEY": settings.GEMINI_API_KEY,
            "OPENAI_API_KEY": settings.OPENAI_API_KEY,
            "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
            "GROQ_API_KEY": settings.GROQ_API_KEY,
            "OPENAI_API_BASE": settings.OPENAI_API_BASE,
        }
        for env_var, setting_val in key_mappings.items():
            if setting_val and not os.environ.get(env_var):
                os.environ[env_var] = setting_val

    def resolve_auto_model(self) -> str:
        """
        Auto-detects the optimal model based on available API keys or local services.
        Ensures users can use OpenRouter, DeepSeek, Groq, local Ollama, etc. seamlessly.
        """
        if settings.DEFAULT_MODEL and settings.DEFAULT_MODEL.lower() != "auto":
            return settings.DEFAULT_MODEL

        # Priority 1: OpenRouter (universal access to DeepSeek, Claude, Llama, Qwen, etc.)
        if os.environ.get("OPENROUTER_API_KEY") or settings.OPENROUTER_API_KEY:
            return "openrouter/deepseek/deepseek-chat"

        # Priority 2: DeepSeek Direct
        if os.environ.get("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY:
            return "deepseek/deepseek-chat"

        # Priority 3: Groq (ultra-fast inference)
        if os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY:
            return "groq/llama-3.3-70b-versatile"

        # Priority 4: OpenAI
        if os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY:
            return "gpt-4o-mini"

        # Priority 5: Anthropic Claude
        if os.environ.get("ANTHROPIC_API_KEY") or settings.ANTHROPIC_API_KEY:
            return "claude-3-5-haiku-20241022"

        # Priority 6: Custom local OpenAI-compatible endpoint (LM Studio, OpenCode, vLLM)
        if os.environ.get("OPENAI_API_BASE") or settings.OPENAI_API_BASE:
            return "openai/default"

        # Priority 7: Google Gemini
        if os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY:
            return "gemini/gemini-2.5-flash"

        # Default fallback
        return "gemini/gemini-2.5-flash"

    def get_model_for_role(self, role: str) -> str:
        """Returns the configured model string for a given agent role."""
        role_lower = role.lower()
        configured = settings.IDEATOR_MODEL
        if role_lower == "ideator":
            configured = settings.IDEATOR_MODEL
        elif role_lower == "reviewer":
            configured = settings.REVIEWER_MODEL
        elif role_lower == "coder":
            configured = settings.CODER_MODEL
        elif role_lower == "synthesizer":
            configured = settings.SYNTHESIZER_MODEL

        if configured == "auto" or not configured:
            return self.resolve_auto_model()
        return configured

    def generate(
        self,
        role: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        model_override: Optional[str] = None,
    ) -> str:
        """
        Executes a completion request for a specified persona role.
        """
        self._sync_env_keys()
        model = model_override or self.get_model_for_role(role)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # If targeting Ollama, attach api_base if configured
        if model.startswith("ollama/"):
            kwargs["api_base"] = settings.OLLAMA_API_BASE
        elif settings.OPENAI_API_BASE and (model.startswith("openai/") or "/" not in model):
            kwargs["api_base"] = settings.OPENAI_API_BASE

        try:
            response = completion(**kwargs)
            content = response.choices[0].message.content
            return content or ""
        except Exception as e:
            err_str = str(e)
            hint = ""
            if "API key" in err_str or "AuthenticationError" in err_str:
                hint = (
                    "\n[Hint] Make sure your API key is set in .env or environment.\n"
                    "You can use ANY provider: OpenRouter (OPENROUTER_API_KEY), DeepSeek (DEEPSEEK_API_KEY), "
                    "Groq (GROQ_API_KEY), Gemini (GEMINI_API_KEY), OpenAI (OPENAI_API_KEY), Anthropic (ANTHROPIC_API_KEY), "
                    "or run 100% offline with Ollama (ollama/deepseek-r1)."
                )
            raise RuntimeError(
                f"[LLMRouter Error] Failed to generate completion using role='{role}' (model='{model}'): {err_str}{hint}"
            ) from e

    def generate_json(
        self,
        role: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Generates and parses a structured JSON response.
        Extracts JSON from markdown code fences if present.
        """
        raw_response = self.generate(
            role=role,
            system_prompt=system_prompt + "\nYou MUST reply with valid JSON only. Do not add prose outside JSON.",
            user_prompt=user_prompt,
            temperature=temperature,
        )

        # Regex to strip markdown code blocks if the model wrapped it in ```json ... ```
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_response)
        if json_match:
            clean_str = json_match.group(1).strip()
        else:
            clean_str = raw_response.strip()

        try:
            return json.loads(clean_str)
        except json.JSONDecodeError as e:
            # Attempt basic bracket extraction
            start = clean_str.find("{")
            end = clean_str.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(clean_str[start : end + 1])
                except Exception:
                    pass
            raise ValueError(f"Failed to parse model output as JSON: {raw_response[:300]}...") from e


router = LLMRouter()
