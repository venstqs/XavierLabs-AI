import os
import json
import re
import time
from typing import Any, Dict, List, Optional
import litellm
from litellm import completion
from xavierlabs.config import settings

# Silence unnecessary litellm telemetry in terminal
litellm.telemetry = False
litellm.drop_params = True
litellm.suppress_debug_info = True


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
            if setting_val:
                clean_val = setting_val.strip("'\" \t\r\n")
                os.environ[env_var] = clean_val
            elif os.environ.get(env_var):
                os.environ[env_var] = os.environ[env_var].strip("'\" \t\r\n")

        # Google Gemini SDK checks both GEMINI_API_KEY and GOOGLE_API_KEY
        if os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
        elif os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

    def is_ollama_reachable(self) -> bool:
        """Quick check if local Ollama daemon is active and responding."""
        import urllib.request
        try:
            url = f"{settings.OLLAMA_API_BASE}/api/tags"
            req = urllib.request.Request(url, headers={"User-Agent": "xavierlabs"})
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def resolve_auto_model(self) -> str:
        """
        Auto-detects the optimal model based on available API keys or local services.
        Ensures users can use Groq, OpenRouter, DeepSeek, local Ollama, etc. seamlessly.
        """
        # If DEFAULT_MODEL is explicitly set to Ollama, check if Ollama is actually reachable
        if settings.DEFAULT_MODEL and settings.DEFAULT_MODEL.lower() != "auto":
            if settings.DEFAULT_MODEL.startswith("ollama/") and not self.is_ollama_reachable():
                # Ollama is not running; fall through to available cloud keys
                pass
            else:
                return settings.DEFAULT_MODEL

        # Priority 1: Groq (ultra-fast inference with high token limits)
        if os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY:
            return "groq/groq/compound-mini"

        # Priority 2: OpenRouter (universal access to DeepSeek, Claude, Llama, Qwen, etc.)
        if os.environ.get("OPENROUTER_API_KEY") or settings.OPENROUTER_API_KEY:
            return "openrouter/deepseek/deepseek-chat"

        # Priority 3: DeepSeek Direct
        if os.environ.get("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY:
            return "deepseek/deepseek-chat"

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

        # Fallback to local Ollama if running, otherwise default to Gemini
        if self.is_ollama_reachable():
            return "ollama/deepseek-r1"

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

    def validate_provider_keys(self, model: str) -> Optional[str]:
        """
        Validates that credentials exist for the chosen model before firing an HTTP request.
        Returns None if valid, or a descriptive error string if missing.
        """
        model_lower = model.lower()

        # Local Ollama check
        if model_lower.startswith("ollama/"):
            if not self.is_ollama_reachable():
                return (
                    f"Could not connect to local Ollama at {settings.OLLAMA_API_BASE}.\n"
                    "Make sure Ollama is installed and running (`ollama run deepseek-r1`), "
                    "or configure a cloud provider like Groq, OpenRouter, or Gemini (`xavier auth`)."
                )
            return None

        if settings.OPENAI_API_BASE and (model_lower.startswith("openai/") or "/" not in model_lower):
            return None

        if model_lower.startswith("groq/") and not (os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY):
            return "Missing GROQ_API_KEY. Please set GROQ_API_KEY in your .env file or run `xavier auth`."

        if (model_lower.startswith("gpt-") or model_lower.startswith("openai/")) and not (os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY):
            return "Missing OPENAI_API_KEY. Please set OPENAI_API_KEY in your .env file."

        if (model_lower.startswith("claude-") or model_lower.startswith("anthropic/")) and not (os.environ.get("ANTHROPIC_API_KEY") or settings.ANTHROPIC_API_KEY):
            return "Missing ANTHROPIC_API_KEY. Please set ANTHROPIC_API_KEY in your .env file."

        if model_lower.startswith("gemini/") and not (os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY):
            return (
                "No active LLM API key detected!\n"
                "XavierLabs defaulted to 'gemini/gemini-2.5-flash', but GEMINI_API_KEY is not set.\n\n"
                "You can use ANY provider you prefer:\n"
                "  • OpenRouter: echo \"OPENROUTER_API_KEY=sk-or-...\" > .env\n"
                "  • DeepSeek:   echo \"DEEPSEEK_API_KEY=sk-...\" > .env\n"
                "  • Ollama:     ollama run deepseek-r1 (100% free offline, zero keys needed!)\n"
                "  • Gemini:     echo \"GEMINI_API_KEY=AIzaSy...\" > .env\n"
                "  • Groq:       echo \"GROQ_API_KEY=gsk_...\" > .env\n"
            )

        return None

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

        validation_err = self.validate_provider_keys(model)
        if validation_err:
            raise RuntimeError(validation_err)

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

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = completion(**kwargs)
                content = response.choices[0].message.content
                return content or ""
            except Exception as e:
                err_str = str(e)
                is_rate_limit = "RateLimitError" in err_str or "rate_limit_exceeded" in err_str or "429" in err_str

                # If rate limited, attempt automatic sliding-window wait before failing
                if is_rate_limit and attempt < max_retries - 1:
                    match = re.search(r"try again in ([\d\.]+)s", err_str, re.IGNORECASE)
                    wait_secs = float(match.group(1)) + 1.0 if match else (12.0 * (attempt + 1))
                    wait_secs = min(max(wait_secs, 3.0), 30.0)

                    try:
                        from rich.console import Console
                        c = Console()
                        c.print(f"[dim yellow]⏳ Provider rate limit reached. Waiting {wait_secs:.1f}s for quota replenishment before resuming...[/dim yellow]")
                    except Exception:
                        pass

                    time.sleep(wait_secs)
                    continue

                # Automatic fallback if a specific Groq model hits OTPM free-tier limit
                if is_rate_limit and model.startswith("groq/") and model != "groq/groq/compound-mini":
                    try:
                        kwargs["model"] = "groq/groq/compound-mini"
                        fallback_res = completion(**kwargs)
                        fallback_content = fallback_res.choices[0].message.content
                        return fallback_content or ""
                    except Exception:
                        pass

                hint = ""
                if is_rate_limit:
                    hint = (
                        "\n[Rate Limit Hint] The free tier token limit was reached for this model.\n"
                        "Wait 30-60 seconds, or switch to another provider: OpenRouter (OPENROUTER_API_KEY), "
                        "DeepSeek (DEEPSEEK_API_KEY), Gemini (GEMINI_API_KEY), or 100% offline Ollama (`ollama run deepseek-r1`)."
                    )
                elif "API key" in err_str or "AuthenticationError" in err_str:
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
