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
# XavierLabs VS Code Dark+ terminal theme
# Mirrors the syntax-highlighted palette on the XavierLabs web workbench.
# ---------------------------------------------------------------------------
SYN_KW = "#569cd6"      # keyword blue
SYN_FN = "#dcdcaa"      # function / agent yellow
SYN_STR = "#ce9178"     # string / artifact coral
SYN_VAR = "#9cdcfe"     # variable / field sky-blue
SYN_TYPE = "#4ec9b0"    # type / ready / passed teal
SYN_FLAG = "#c586c0"    # stage index / flag purple
SYN_NUM = "#b5cea8"     # numeric metric mint
SYN_ERR = "#f48771"     # error coral-red
SYN_COMMENT = "#6a9955" # comment green

LIVE = SYN_TYPE
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
        header_style=MUTED,
        show_header=True,
        pad_edge=False,
    )


class TerminalUI:
    """
    Terminal interface for XavierLabs AI: renders agent transitions,
    sandbox telemetry, and research artifacts with VS Code Dark+ syntax tokens.
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
            Text.assemble((mark[0], f"bold {SYN_VAR}"), "  ", ("XavierLabs", "bold white")),
            Text.assemble((mark[1], f"bold {SYN_VAR}"), "  ", ("autonomous computational research", MUTED)),
            Text.assemble(
                (mark[2], f"bold {SYN_VAR}"),
                " ",
                ("●", SYN_TYPE),
                (" ready · ", MUTED),
                (f"v{__version__}", SYN_NUM),
            ),
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
            f"[{SYN_FLAG}]{step}[/]  [bold {SYN_FN}]{name}[/]",
            align="left",
            style=LINE,
        )
        self.console.print(f"[{SYN_VAR}]●[/] {action}")

    def print_hypothesis(self, hypothesis: Any):
        table = _table("Hypothesis")
        table.add_column("Field", style=SYN_VAR, width=20, no_wrap=True)
        table.add_column("Details")

        table.add_row("Title", f"[bold white]{hypothesis.title}[/bold white]")
        table.add_row("Motivation", hypothesis.motivation)
        table.add_row("Theoretical basis", hypothesis.theoretical_basis)
        table.add_row("Metrics", f"[{SYN_STR}]{', '.join(hypothesis.metrics)}[/]")
        table.add_row("Design", hypothesis.experimental_design)

        self.console.print(table)

    def print_review(self, review: Any):
        status = f"[bold {SYN_TYPE}]approved[/]" if review.approved else f"[bold {SYN_ERR}]needs revision[/]"
        table = _table(f"Peer review · {status}")
        table.add_column("Criterion", style=SYN_VAR)
        table.add_column("Score", justify="right", style=SYN_NUM)
        table.add_column("", min_width=12)

        def bar(score: float, fill_color: str = SYN_TYPE) -> str:
            filled = max(0, min(10, round(score)))
            return f"[bold {fill_color}]{'━' * filled}[/][{LINE}]{'━' * (10 - filled)}[/]"

        for label, score in (
            ("Novelty", review.novelty_score),
            ("Rigor", review.rigor_score),
            ("Feasibility", review.feasibility_score),
        ):
            table.add_row(label, f"{score:.1f}", bar(score, SYN_TYPE))
        table.add_row(
            "[bold white]Overall[/bold white]",
            f"[bold {SYN_NUM}]{review.overall_score:.1f}[/]",
            bar(review.overall_score, SYN_FN),
        )

        self.console.print(table)
        if review.weaknesses:
            self.console.print(f"[{SYN_FN}]Weaknesses:[/] {', '.join(review.weaknesses)}")
        if review.modifications_required:
            self.console.print(f"[{MUTED}]Requested changes: {review.modifications_required}[/]")

    def print_execution_telemetry(self, result: Any, iteration: int):
        color = SYN_TYPE if result.success else SYN_ERR
        if result.success:
            state = "passed"
        elif result.returncode == 0:
            state = "failed · no metrics.json"
        else:
            state = f"failed · exit {result.returncode}"
        title = (
            f"[{color}]●[/] [bold white]Run #{iteration}[/bold white] "
            f"[{MUTED}]{state} · [/][{SYN_NUM}]{result.execution_time:.2f}s[/]"
            f"[{MUTED}] · {result.sandbox_type}[/]"
        )

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
                body.append(k, style=SYN_VAR)
                body.append(f"  {shown}", style=SYN_NUM)
                if i < len(lines) - 1:
                    body.append("\n")

        if not result.success and result.error_traceback:
            body.append("\n\n" if body else "")
            body.append(result.error_traceback.strip()[-1500:], style=SYN_ERR)
        elif not result.metrics and result.stdout:
            body.append(result.stdout.strip()[-400:], style=MUTED)

        self.console.print(Panel(
            body if body else Text("no output", style=MUTED),
            title=title,
            title_align="left",
            border_style=LINE if result.success else SYN_ERR,
            box=box.ROUNDED,
            padding=(0, 1),
        ))

    def print_artifacts_summary(self, artifacts: Dict[str, str]):
        paths = [Path(p) for p in artifacts.values() if p and p != "N/A"]
        root = paths[0].parent if paths else None
        table = _table("Artifacts")
        table.add_column("Type", style=SYN_VAR, no_wrap=True)
        table.add_column("File", style=SYN_STR)

        for atype, path in artifacts.items():
            shown = path
            if root and path != "N/A" and Path(path).parent == root:
                shown = Path(path).name
            table.add_row(atype, shown)

        self.console.print(table)
        if root:
            self.console.print(f"[{MUTED}]Artifacts in [/][{SYN_STR}]{root}[/]")

    def print_markdown(self, md_text: str):
        self.console.print(Markdown(md_text))


ui = TerminalUI()
