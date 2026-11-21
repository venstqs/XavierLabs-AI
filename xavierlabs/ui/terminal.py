import sys
from pathlib import Path
from typing import Any, Dict

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from xavierlabs import __version__

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(legacy_windows=False)

# ---------------------------------------------------------------------------
# XavierLabs terminal theme
# Monochrome ink on the terminal's own background, a single green "live" accent,
# and red/yellow reserved for failures and warnings. Mirrors the XavierLabs web brand.
# ---------------------------------------------------------------------------
LIVE = "green"
LINE = "grey27"
MUTED = "grey58"
TABLE_BOX = box.SIMPLE_HEAD

# Small rendition of the XavierLabs mark (a slanted "A" with a crossbar)
MARK = ("  ╱╲ ", " ╱──╲", "╱    ╲")
MARK_ASCII = ("  /\\ ", " /--\\", "/    \\")

STEPS = {
    "ideator": "01",
    "reviewer": "02",
    "coder": "03",
    "system": "04",
    "synthesizer": "05",
}


def _table(title: str = "") -> Table:
    return Table(
        title=f"[bold]{title}[/bold]" if title else None,
        title_justify="left",
        box=TABLE_BOX,
        border_style=LINE,
        header_style=f"{MUTED}",
        show_header=True,
        pad_edge=False,
    )


class TerminalUI:
    """
    Terminal interface for XavierLabs AI: renders agent transitions,
    sandbox telemetry, and research artifacts in the XavierLabs style.
    """

    def __init__(self):
        self.console = console

    def print_banner(self):
        try:
            "".join(MARK).encode(self.console.encoding or "utf-8")
            mark = MARK
        except (UnicodeEncodeError, LookupError):
            mark = MARK_ASCII

        lines = [
            Text.assemble((mark[0], "bold"), "  ", ("XavierLabs", "bold")),
            Text.assemble((mark[1], "bold"), "  ", ("autonomous computational research", MUTED)),
            Text.assemble((mark[2], "bold"), " ", ("●", LIVE), (f" ready · v{__version__}", MUTED)),
        ]
        self.console.print()
        for line in lines:
            self.console.print(line)
        self.console.print()

    def print_agent_header(self, agent_name: str, role: str, action: str):
        step = STEPS.get(role.lower(), "··")
        name = agent_name.replace("The ", "")
        self.console.print()
        self.console.rule(
            f"[{MUTED}]{step}[/]  [bold]{name}[/bold]",
            align="left",
            style=LINE,
        )
        self.console.print(f"[{LIVE}]●[/] {action}")

    def print_hypothesis(self, hypothesis: Any):
        table = _table("Hypothesis")
        table.add_column("Field", style=MUTED, width=20, no_wrap=True)
        table.add_column("Details")

        table.add_row("Title", f"[bold]{hypothesis.title}[/bold]")
        table.add_row("Motivation", hypothesis.motivation)
        table.add_row("Theoretical basis", hypothesis.theoretical_basis)
        table.add_row("Metrics", ", ".join(hypothesis.metrics))
        table.add_row("Design", hypothesis.experimental_design)

        self.console.print(table)

    def print_review(self, review: Any):
        status = f"[bold {LIVE}]approved[/]" if review.approved else "[bold red]needs revision[/]"
        table = _table(f"Peer review · {status}")
        table.add_column("Criterion", style=MUTED)
        table.add_column("Score", justify="right")
        table.add_column("", min_width=12)

        def bar(score: float) -> str:
            filled = max(0, min(10, round(score)))
            return f"[bold]{'━' * filled}[/][{LINE}]{'━' * (10 - filled)}[/]"

        for label, score in (
            ("Novelty", review.novelty_score),
            ("Rigor", review.rigor_score),
            ("Feasibility", review.feasibility_score),
        ):
            table.add_row(label, f"{score:.1f}", bar(score))
        table.add_row("[bold]Overall[/bold]", f"[bold]{review.overall_score:.1f}[/bold]", bar(review.overall_score))

        self.console.print(table)
        if review.weaknesses:
            self.console.print(f"[yellow]Weaknesses:[/yellow] {', '.join(review.weaknesses)}")
        if review.modifications_required:
            self.console.print(f"[{MUTED}]Requested changes: {review.modifications_required}[/]")

    def print_execution_telemetry(self, result: Any, iteration: int):
        color = LIVE if result.success else "red"
        if result.success:
            state = "passed"
        elif result.returncode == 0:
            state = "failed · no metrics.json"
        else:
            state = f"failed · exit {result.returncode}"
        title = f"[{color}]●[/] [bold]Run #{iteration}[/bold] [{MUTED}]{state} · {result.execution_time:.2f}s · {result.sandbox_type}[/]"

        body = Text()
        if result.metrics:
            width = min(28, max(len(str(k)) for k in result.metrics))
            lines = []
            for k, v in result.metrics.items():
                shown = str(v)
                if len(shown) > 120:
                    shown = shown[:117] + "..."
                lines.append((str(k).ljust(width), shown))
            for i, (k, shown) in enumerate(lines):
                body.append(k, style=MUTED)
                body.append(f"  {shown}" + ("\n" if i < len(lines) - 1 else ""))

        if not result.success and result.error_traceback:
            body.append("\n\n" if body else "")
            body.append(result.error_traceback.strip()[-1500:], style="red")
        elif not result.metrics and result.stdout:
            body.append(result.stdout.strip()[-400:], style=MUTED)

        self.console.print(Panel(
            body if body else Text("no output", style=MUTED),
            title=title,
            title_align="left",
            border_style=LINE if result.success else "red",
            box=box.ROUNDED,
            padding=(0, 1),
        ))

    def print_artifacts_summary(self, artifacts: Dict[str, str]):
        paths = [Path(p) for p in artifacts.values() if p and p != "N/A"]
        root = paths[0].parent if paths else None
        table = _table("Artifacts")
        table.add_column("Type", style=MUTED, no_wrap=True)
        table.add_column("File")

        for atype, path in artifacts.items():
            shown = path
            if root and path != "N/A" and Path(path).parent == root:
                shown = Path(path).name
            table.add_row(atype, shown)

        self.console.print(table)
        if root:
            self.console.print(f"[{MUTED}]in {root}[/]")

    def print_markdown(self, md_text: str):
        self.console.print(Markdown(md_text))


ui = TerminalUI()
