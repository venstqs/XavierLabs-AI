import io
import time
from pathlib import Path
from typing import Optional

from xavierlabs.sandbox.base import SandboxBase, ExecutionResult
from xavierlabs.config import settings


# Image built on first use when DOCKER_IMAGE is left at its default.
# The stock python:*-slim images ship without numpy/matplotlib, which nearly
# every generated experiment and plot.py needs, and the sandbox runs offline.
MANAGED_IMAGE_TAG = "xavierlabs-sandbox:latest"
MANAGED_IMAGE_DOCKERFILE = """\
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 MPLBACKEND=Agg PIP_NO_CACHE_DIR=1
RUN pip install --quiet numpy scipy pandas matplotlib seaborn scikit-learn sympy networkx
WORKDIR /workspace
"""


class DockerSandbox(SandboxBase):
    """
    Docker SDK sandbox providing containerized ephemeral execution.
    Mounts the experiment workspace into an isolated, network-disabled,
    resource-limited container.
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

    def ensure_image(self) -> None:
        """Pulls or builds the sandbox image if it is not present locally."""
        import docker

        client = self._get_client()
        try:
            client.images.get(self.image)
            return
        except docker.errors.ImageNotFound:
            pass

        if self.image == MANAGED_IMAGE_TAG:
            client.images.build(
                fileobj=io.BytesIO(MANAGED_IMAGE_DOCKERFILE.encode("utf-8")),
                tag=MANAGED_IMAGE_TAG,
                rm=True,
            )
        else:
            client.images.pull(self.image)

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

        try:
            self.ensure_image()
        except Exception as e:
            msg = f"Could not prepare Docker image '{self.image}': {e}"
            return ExecutionResult(
                returncode=-1, stdout="", stderr=msg, execution_time=0.0,
                success=False, error_traceback=msg, sandbox_type="docker_container",
            )

        client = self._get_client()
        error_traceback: Optional[str] = None
        stdout, stderr = "", ""
        container = None
        start_time = time.time()
        try:
            container = client.containers.run(
                image=self.image,
                command=["python", f"/workspace/{script_path.name}"],
                volumes={str(workspace_dir): {"bind": "/workspace", "mode": "rw"}},
                working_dir="/workspace",
                environment={"PYTHONUNBUFFERED": "1", "MPLBACKEND": "Agg"},
                detach=True,
                network_mode=settings.DOCKER_NETWORK,
                mem_limit=settings.DOCKER_MEM_LIMIT,
                nano_cpus=int(settings.DOCKER_CPUS * 1e9),
                pids_limit=256,
            )

            try:
                result = container.wait(timeout=timeout)
                returncode = result.get("StatusCode", 0)
                timed_out = False
            except Exception:
                # docker-py raises a requests ReadTimeout/ConnectionError on timeout
                timed_out = True
                returncode = -1
                try:
                    container.kill()
                except Exception:
                    pass

            execution_time = time.time() - start_time
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")

            if timed_out:
                stderr = (stderr + f"\nExecution timed out after {timeout} seconds.").strip()
            elif returncode == 137:
                stderr = (stderr + f"\nContainer was killed (exit 137), likely out of memory "
                                   f"(limit {settings.DOCKER_MEM_LIMIT}).").strip()

            success = (returncode == 0)
            if not success:
                error_traceback = stderr.strip() or stdout.strip()

        except Exception as e:
            execution_time = time.time() - start_time
            stderr = f"Docker execution error: {str(e)}"
            returncode = -1
            success = False
            error_traceback = stderr

        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

        return ExecutionResult(
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            success=success,
            metrics=self._read_metrics(workspace_dir),
            error_traceback=error_traceback,
            sandbox_type="docker_container",
        )
