import sys
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(legacy_windows=False)

PIXEL_BANNER_BLOCK = r"""
                        █                   ██           █            
                                             █           █            
 █   █   ████  ██ ██   ██     ███   █ ██     █     ████  ████    ████ 
  █ █   █   █   █ █     █    █   █  ██       █    █   █  █   █  █     
   █    █   █   █ █     █    █████  █        █    █   █  █   █   ███  
  █ █   █  ██    █      █    █      █        █    █  ██  █   █      █ 
 █   █   ██ █    █     ███    ███   █       ███    ██ █  ████   ████  
"""

PIXEL_BANNER_ASCII = r"""
                        #                   ##           #            
                                             #           #            
 #   #   ####  ## ##   ##     ###   # ##     #     ####  ####    #### 
  # #   #   #   # #     #    #   #  ##       #    #   #  #   #  #     
   #    #   #   # #     #    #####  #        #    #   #  #   #   ###  
  # #   #  ##    #      #    #      #        #    #  ##  #   #      # 
 #   #   ## #    #     ###    ###   #       ###    ## #  ####   ####  
"""


class TerminalUI:
    """
    Feynman-Style Reactive Terminal Interface for XavierLabs AI.
    Renders live telemetry, agent transitions, and scientific artifacts.
    """

    def __init__(self):
        self.console = console

    def print_banner(self):
        try:
            self.console.print(PIXEL_BANNER_BLOCK, style="bold #9ec97b")
        except UnicodeEncodeError:
            self.console.print(PIXEL_BANNER_ASCII, style="bold #9ec97b")

        self.console.print(
            "[bold #9ec97b]x a v i e r l a b s[/] [dim]•[/] [dim #a3c983]terminal-native computational research swarm[/]\n",
            justify="center",
        )

    def print_agent_header(self, agent_name: str, role: str, action: str):
        colors = {
            "ideator": "cyan",
            "reviewer": "yellow",
            "coder": "green",
            "synthesizer": "magenta",
            "system": "blue",
        }
        color = colors.get(role.lower(), "white")
        badge = f"[{color} bold]● {agent_name.upper()} ({role.upper()})[/]"
        self.console.print(Panel(f"{action}", title=badge, border_style=color))

    def print_hypothesis(self, hypothesis: Any):
        table = Table(title="[bold cyan]Generated Computational Hypothesis[/bold cyan]", show_header=True)
        table.add_column("Field", style="dim", width=20)
        table.add_column("Details", style="white")

        table.add_row("Title", hypothesis.title)
        table.add_row("Motivation", hypothesis.motivation)
        table.add_row("Theoretical Basis", hypothesis.theoretical_basis)
        table.add_row("Expected Metrics", ", ".join(hypothesis.metrics))
        table.add_row("Experimental Design", hypothesis.experimental_design)

        self.console.print(table)

    def print_review(self, review: Any):
        status = "[bold green]APPROVED[/bold green]" if review.approved else "[bold red]REJECTED (NEEDS REVISION)[/bold red]"
        table = Table(title=f"Peer Review Assessment: {status}", show_header=True)
        table.add_column("Criterion", style="dim")
        table.add_column("Score (1-10)", justify="center")

        table.add_row("Novelty", f"{review.novelty_score:.1f}/10")
        table.add_row("Theoretical Rigor", f"{review.rigor_score:.1f}/10")
        table.add_row("Feasibility", f"{review.feasibility_score:.1f}/10")
        table.add_row("[bold]Overall Score[/bold]", f"[bold]{review.overall_score:.1f}/10[/bold]")

        self.console.print(table)
        if review.weaknesses:
            self.console.print(f"[yellow]Identified Weaknesses/Risks:[/yellow] {', '.join(review.weaknesses)}")
        if review.modifications_required:
            self.console.print(f"[dim]Modifications Required: {review.modifications_required}[/dim]")

    def print_execution_telemetry(self, result: Any, iteration: int):
        status_color = "green" if result.success else "red"
        title = f"[bold {status_color}]Sandbox Run #{iteration} Telemetry ({result.sandbox_type})[/bold {status_color}]"

        content = f"[bold]Duration:[/bold] {result.execution_time:.2f}s | [bold]Return Code:[/bold] {result.returncode}\n\n"
        if result.metrics:
            content += f"[bold green]Parsed Metrics:[/bold green]\n"
            for k, v in result.metrics.items():
                content += f"  • {k}: {v}\n"

        if not result.success and result.error_traceback:
            content += f"\n[bold red]Error / Traceback:[/bold red]\n[dim]{result.error_traceback}[/dim]"
        elif result.stdout:
            content += f"\n[dim bold]Stdout (truncated):[/dim bold]\n[dim]{result.stdout[-400:]}[/dim]"

        self.console.print(Panel(content, title=title, border_style=status_color))

    def print_artifacts_summary(self, artifacts: Dict[str, str]):
        table = Table(title="[bold magenta]Compiled Research Artifacts[/bold magenta]", show_header=True)
        table.add_column("Artifact Type", style="cyan")
        table.add_column("File Location", style="white")

        for atype, path in artifacts.items():
            table.add_row(atype, path)

        self.console.print(table)

    def print_markdown(self, md_text: str):
        self.console.print(Markdown(md_text))


ui = TerminalUI()
