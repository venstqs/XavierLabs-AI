from typing import Tuple
from xavierlabs.config import settings
from xavierlabs.sandbox.base import SandboxBase
from xavierlabs.sandbox.local_sandbox import LocalSandbox
from xavierlabs.sandbox.docker_sandbox import DockerSandbox


def get_sandbox() -> Tuple[SandboxBase, str]:
    """
    Returns an appropriate sandbox instance and an informative description of its status.
    Respects settings.SANDBOX_MODE ("auto", "docker", "local").
    """
    mode = settings.SANDBOX_MODE.lower()

    if mode == "docker":
        docker_box = DockerSandbox()
        if docker_box.is_available():
            return docker_box, f"Docker Container ({settings.DOCKER_IMAGE})"
        raise RuntimeError("Docker sandbox was explicitly requested, but Docker daemon is not accessible.")

    if mode == "local":
        return LocalSandbox(), "Local Isolated Subprocess Sandbox"

    # Auto mode: check Docker first, gracefully fall back to local
    try:
        docker_box = DockerSandbox()
        if docker_box.is_available():
            return docker_box, f"Docker Container ({settings.DOCKER_IMAGE})"
    except Exception:
        pass

    return LocalSandbox(), "Local Isolated Subprocess Sandbox (Fallback)"
