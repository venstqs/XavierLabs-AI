import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

from xavierlabs.sandbox.base import SandboxBase, ExecutionResult, scrubbed_env
from xavierlabs.config import settings


class LocalSandbox(SandboxBase):
    """
    Subprocess sandbox that runs Python code in a separate process with
    working directory containment, a scrubbed environment (no API keys),
    and strict timeout enforcement.

    Note: this is process isolation only. Generated code can still read and
    write files the current user can access. Use the Docker sandbox for
    stronger isolation.
    """

    def __init__(self, python_executable: Optional[str] = None):
        self.python_executable = python_executable or sys.executable

    def is_available(self) -> bool:
        return Path(self.python_executable).exists()

    def run_script(
        self,
        script_path: Path,
        workspace_dir: Path,
        timeout: Optional[int] = None,
        clear_metrics: bool = True,
    ) -> ExecutionResult:
        timeout = timeout or settings.EXECUTION_TIMEOUT
        workspace_dir = Path(workspace_dir).resolve()
        script_path = Path(script_path).resolve()

        if clear_metrics:
            self._clear_metrics(workspace_dir)

        error_traceback: Optional[str] = None

        env = scrubbed_env()
        # Set unbuffered output so stdout/stderr can be captured reliably
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONPATH"] = str(workspace_dir)
        # Headless plotting backend so matplotlib never tries to open a window
        env["MPLBACKEND"] = "Agg"

        start_time = time.time()
        try:
            process = subprocess.run(
                [self.python_executable, str(script_path)],
                cwd=str(workspace_dir),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
            execution_time = time.time() - start_time
            stdout = process.stdout
            stderr = process.stderr
            returncode = process.returncode
            success = (returncode == 0)

            if not success:
                error_traceback = self._extract_traceback(stderr or stdout)

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            partial = e.stdout or ""
            stdout = partial.decode("utf-8", errors="replace") if isinstance(partial, bytes) else partial
            stderr = f"Execution timed out after {timeout} seconds."
            returncode = -1
            success = False
            error_traceback = stderr

        except Exception as e:
            execution_time = time.time() - start_time
            stdout = ""
            stderr = f"Sandbox execution error: {str(e)}"
            returncode = -1
            success = False
            error_traceback = stderr

        return ExecutionResult(
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            success=success,
            metrics=self._read_metrics(workspace_dir),
            error_traceback=error_traceback,
            sandbox_type="local_subprocess",
        )

    def _extract_traceback(self, output: str) -> str:
        """Extracts the most relevant Python traceback from stderr/stdout."""
        if "Traceback (most recent call last):" in output:
            parts = output.split("Traceback (most recent call last):")
            return "Traceback (most recent call last):" + parts[-1].strip()
        return output.strip()
