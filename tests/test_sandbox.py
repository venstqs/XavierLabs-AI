import json
import pytest
from pathlib import Path
from xavierlabs.sandbox.local_sandbox import LocalSandbox


def test_local_sandbox_success(tmp_path: Path):
    sandbox = LocalSandbox()
    script = tmp_path / "test_success.py"
    script.write_text(
        """
import json
print("Telemetry stdout line 1")
metrics = {"accuracy": 0.95, "loss": 0.05}
with open("metrics.json", "w") as f:
    json.dump(metrics, f)
print("Finished experiment cleanly")
"""
    )

    result = sandbox.run_script(script, tmp_path, timeout=10)
    assert result.success is True
    assert result.returncode == 0
    assert "Telemetry stdout" in result.stdout
    assert result.metrics == {"accuracy": 0.95, "loss": 0.05}
    assert result.error_traceback is None


def test_local_sandbox_failure_traceback(tmp_path: Path):
    sandbox = LocalSandbox()
    script = tmp_path / "test_crash.py"
    script.write_text(
        """
print("Starting before crash...")
x = 10 / 0
"""
    )

    result = sandbox.run_script(script, tmp_path, timeout=10)
    assert result.success is False
    assert result.returncode != 0
    assert result.error_traceback is not None
    assert "ZeroDivisionError" in result.error_traceback


def test_local_sandbox_timeout(tmp_path: Path):
    sandbox = LocalSandbox()
    script = tmp_path / "test_hang.py"
    script.write_text(
        """
import time
time.sleep(5)
"""
    )

    result = sandbox.run_script(script, tmp_path, timeout=1)
    assert result.success is False
    assert "timed out" in (result.stderr or "").lower()
