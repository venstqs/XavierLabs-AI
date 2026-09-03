import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from xavierlabs.sandbox.base import SandboxBase, ExecutionResult
from xavierlabs.config import settings


class DockerSandbox(SandboxBase):
    """
    Docker SDK sandbox providing containerized ephemeral execution.
    Mounts the experiment workspace into an isolated container.
    """

    def __init__(self, image: Optional[str] = None):
        self.image = image or settings.DOCKER_IMAGE
        self._client = None

    def _get_client(self):
        if self._client is None:
            import docker
            self._client = docker.from_env()
        return self._client

    def is_available(self) -> bool:
        try:
            client = self._get_client()
            client.ping()
            return True
        except Exception:
            return False

    def run_script(
        self,
        script_path: Path,
        workspace_dir: Path,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        timeout = timeout or settings.EXECUTION_TIMEOUT
        workspace_dir = Path(workspace_dir).resolve()
        script_path = Path(script_path).resolve()

        client = self._get_client()
        start_time = time.time()
        metrics: Dict[str, Any] = {}
        error_traceback: Optional[str] = None

        container = None
        try:
            # Mount workspace_dir to /workspace inside container
            volumes = {
                str(workspace_dir): {
                    "bind": "/workspace",
                    "mode": "rw"
                }
            }

            container = client.containers.run(
                image=self.image,
                command=f"python /workspace/{script_path.name}",
                volumes=volumes,
                working_dir="/workspace",
                detach=True,
                remove=False,
                network_mode="bridge",
            )

            # Wait for completion or timeout
            result = container.wait(timeout=timeout)
            execution_time = time.time() - start_time
            returncode = result.get("StatusCode", 0)

            # Retrieve stdout & stderr
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="ignore")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="ignore")
            success = (returncode == 0)

            if not success:
                error_traceback = stderr.strip() or stdout.strip()

        except Exception as e:
            execution_time = time.time() - start_time
            stdout = ""
            stderr = f"Docker execution error or timeout: {str(e)}"
            returncode = -1
            success = False
            error_traceback = stderr

        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

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
            sandbox_type="docker_container",
        )
