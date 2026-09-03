from pathlib import Path
from typing import List, Dict, Optional


class WorkspaceInspector:
    """
    Inspects starting codebases, datasets, or notes provided in the workspace.
    """

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)

    def scan_files(self, max_depth: int = 3, extensions: Optional[List[str]] = None) -> List[Path]:
        """Scans for relevant code and data files in the workspace."""
        if not self.root_dir.exists():
            return []

        if extensions is None:
            extensions = [".py", ".csv", ".json", ".md", ".txt", ".yaml", ".yml", ".ipynb"]

        matches = []
        for path in self.root_dir.rglob("*"):
            if any(part.startswith(".") for part in path.parts):
                continue  # ignore hidden dirs like .venv, .git
            if path.is_file() and path.suffix.lower() in extensions:
                matches.append(path)
        return matches

    def read_code_summary(self, max_chars_per_file: int = 2000) -> str:
        """Generates a concise textual summary of existing files in the workspace."""
        files = self.scan_files()
        if not files:
            return "No existing code or dataset files found in workspace."

        summary_parts = []
        for f in files[:8]:  # Limit to 8 files to avoid blowing up context
            try:
                rel = f.relative_to(self.root_dir)
                content = f.read_text(encoding="utf-8", errors="ignore")
                truncated = content[:max_chars_per_file]
                if len(content) > max_chars_per_file:
                    truncated += "\n... [content truncated] ..."
                summary_parts.append(f"--- File: {rel} ---\n{truncated}\n")
            except Exception:
                continue

        return "\n".join(summary_parts)
