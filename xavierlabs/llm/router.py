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
        if settings.GEMINI_API_KEY and not os.environ.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
        if settings.OPENAI_API_KEY and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        if settings.ANTHROPIC_API_KEY and not os.environ.get("ANTHROPIC_API_KEY"):
            os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
        if settings.GROQ_API_KEY and not os.environ.get("GROQ_API_KEY"):
            os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

    def get_model_for_role(self, role: str) -> str:
        """Returns the configured model string for a given agent role."""
        role_lower = role.lower()
        if role_lower == "ideator":
            return settings.IDEATOR_MODEL
        elif role_lower == "reviewer":
            return settings.REVIEWER_MODEL
        elif role_lower == "coder":
            return settings.CODER_MODEL
        elif role_lower == "synthesizer":
            return settings.SYNTHESIZER_MODEL
        return settings.IDEATOR_MODEL

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

        try:
            response = completion(**kwargs)
            content = response.choices[0].message.content
            return content or ""
        except Exception as e:
            # Provide clear diagnostic context
            raise RuntimeError(
                f"[LLMRouter Error] Failed to generate completion using role='{role}' (model='{model}'): {str(e)}"
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
