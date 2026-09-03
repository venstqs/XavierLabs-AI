from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional


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
    ) -> ExecutionResult:
        """Runs the given Python script within the sandboxed environment."""
        pass
