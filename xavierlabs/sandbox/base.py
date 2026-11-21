import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional


METRICS_FILENAME = "metrics.json"

# Environment variables that must never be exposed to LLM-generated code.
_SENSITIVE_ENV_MARKERS = ("API_KEY", "API_BASE", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")


def scrubbed_env() -> Dict[str, str]:
    """Returns a copy of os.environ with API keys and other secrets removed."""
    return {
        k: v
        for k, v in os.environ.items()
        if not any(marker in k.upper() for marker in _SENSITIVE_ENV_MARKERS)
    }


@dataclass
class ExecutionResult:
    returncode: int
    stdout: str
    stderr: str
    execution_time: float
    success: bool
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_traceback: Optional[str] = None
    sandbox_type: str = "unknown"

    def summary(self) -> str:
        status = "[green]SUCCESS[/green]" if self.success else f"[red]FAILED (code {self.returncode})[/red]"
        return f"Execution: {status} in {self.execution_time:.2f}s via {self.sandbox_type}"


class SandboxBase(ABC):
    """Abstract base class for script execution sandboxes."""

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if this sandbox runtime is functional."""
        pass

    @abstractmethod
    def run_script(
        self,
        script_path: Path,
        workspace_dir: Path,
        timeout: Optional[int] = None,
        clear_metrics: bool = True,
    ) -> ExecutionResult:
        """
        Runs the given Python script within the sandboxed environment.
        If clear_metrics is True, any existing metrics.json is removed first so that
        only metrics written by this run are reported.
        """
        pass

    @staticmethod
    def _clear_metrics(workspace_dir: Path) -> None:
        """Removes metrics left by a previous run so stale results are never reported."""
        try:
            (workspace_dir / METRICS_FILENAME).unlink(missing_ok=True)
        except OSError:
            pass

    @staticmethod
    def _read_metrics(workspace_dir: Path) -> Dict[str, Any]:
        metrics_file = workspace_dir / METRICS_FILENAME
        if metrics_file.exists():
            try:
                data = json.loads(metrics_file.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {"result": data}
            except Exception:
                pass
        return {}
