import sys
import os
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from xavierlabs.sandbox.base import SandboxBase, ExecutionResult
from xavierlabs.config import settings


class LocalSandbox(SandboxBase):
    """
    Subprocess sandbox that runs Python code in an isolated process
    with working directory containment and strict timeout enforcement.
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
    ) -> ExecutionResult:
        timeout = timeout or settings.EXECUTION_TIMEOUT
        workspace_dir = Path(workspace_dir).resolve()
        script_path = Path(script_path).resolve()

        start_time = time.time()
        metrics: Dict[str, Any] = {}
        error_traceback: Optional[str] = None

        env = os.environ.copy()
        # Set unbuffered output so stdout/stderr can be captured reliably
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONPATH"] = str(workspace_dir)

        try:
            process = subprocess.run(
                [self.python_executable, str(script_path.name)],
                cwd=str(workspace_dir),
                env=env,
                capture_output=True,
                text=True,
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
            stdout = e.stdout or ""
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

        # Try to read generated metrics.json
        metrics_file = workspace_dir / "metrics.json"
        if metrics_file.exists():
            try:
                metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        return ExecutionResult(
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            success=success,
            metrics=metrics,
            error_traceback=error_traceback,
            sandbox_type="local_subprocess",
        )

    def _extract_traceback(self, output: str) -> str:
        """Extracts the most relevant Python traceback from stderr/stdout."""
        if "Traceback (most recent call last):" in output:
            parts = output.split("Traceback (most recent call last):")
            return "Traceback (most recent call last):" + parts[-1].strip()
        return output.strip()
