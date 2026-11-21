"""
Test isolation: point the database and experiment workspace at a temporary
directory *before* xavierlabs.config is imported, so the test suite never
writes to the developer's real xavierlabs.db or experiments/ folder.
"""
import os
import tempfile
from pathlib import Path

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="xavierlabs-tests-"))
os.environ["DB_PATH"] = str(_TEST_ROOT / "test.db")
os.environ["WORKSPACE_DIR"] = str(_TEST_ROOT / "experiments")
os.environ["SANDBOX_MODE"] = "local"
