import os
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.table import Table
from rich.panel import Panel

from xavierlabs.config import settings
from xavierlabs.ui.terminal import ui
from xavierlabs.loop.orchestrator import ResearchOrchestrator
from xavierlabs.sandbox.manager import get_sandbox
from xavierlabs.db.session import init_db, engine
from sqlmodel import Session, select
from xavierlabs.db.models import Experiment, RunRecord, ArtifactRecord

app = typer.Typer(
    name="xavier",
    help="XavierLabs AI: Terminal-Native Computational Scientific Research Swarm",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Main callback to show banner if no subcommand provided."""
    if ctx.invoked_subcommand is None:
        ui.print_banner()
        ui.console.print("[yellow]Use [bold]xavier --help[/bold] to see available commands.[/yellow]")


@app.command(name="research")
def research(
    topic: str = typer.Argument(..., help="Research question, hypothesis, or topic to investigate"),
    codebase: Optional[Path] = typer.Option(None, "--codebase", "-c", help="Path to starting codebase or datasets to ingest"),
    retries: int = typer.Option(settings.MAX_DEBUG_RETRIES, "--retries", "-r", help="Max auto-debugging retries for failing experiments"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override LLM model for all agents (e.g. gemini/gemini-2.5-flash)"),
):
    """
    Launch an autonomous end-to-end scientific research loop.
    Discovers literature, formulates hypothesis, peer-reviews, codes experiment.py, executes with auto-debugging, and compiles academic paper.
    """
    if model:
        settings.IDEATOR_MODEL = model
        settings.REVIEWER_MODEL = model
        settings.CODER_MODEL = model
        settings.SYNTHESIZER_MODEL = model

    orchestrator = ResearchOrchestrator()
    orchestrator.run_research(
        topic=topic,
        starting_code_dir=codebase,
        max_debug_retries=retries,
    )


@app.command(name="run")
def run_script(
    script_path: Path = typer.Argument(..., help="Path to the Python experiment script to run"),
    timeout: int = typer.Option(settings.EXPERIMENT_TIMEOUT_SECONDS, "--timeout", "-t", help="Timeout in seconds"),
):
    """
    Execute a standalone experiment script within the isolated XavierLabs sandbox.
    Captures telemetry and parses metrics.json.
    """
    ui.print_banner()
    if not script_path.exists():
        ui.console.print(f"[bold red]Error:[/bold red] Script not found: {script_path}")
        raise typer.Exit(code=1)

    sandbox, desc = get_sandbox()
    ui.console.print(f"[bold green]Running {script_path.name} in {desc}...[/bold green]\n")

    result = sandbox.run_script(script_path, script_path.parent, timeout=timeout)
    ui.print_execution_telemetry(result, iteration=1)

    if result.success:
        ui.console.print("[bold green]✔ Script execution completed successfully.[/bold green]")
    else:
        ui.console.print("[bold red]❌ Script execution failed.[/bold red]")


@app.command(name="history")
def show_history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of past experiments to display")
):
    """
    View the history of autonomous research experiments from the SQLite database.
    """
    ui.print_banner()
    init_db()

    with Session(engine) as session:
        statement = select(Experiment).order_by(Experiment.created_at.desc()).limit(limit)
        experiments = session.exec(statement).all()

        if not experiments:
            ui.console.print("[yellow]No research experiments recorded yet in the database.[/yellow]")
            return

        table = Table(title="[bold cyan]XavierLabs AI Research History[/bold cyan]", show_header=True)
        table.add_column("ID", style="dim", width=6)
        table.add_column("Date", style="dim", width=18)
        table.add_column("Topic", style="white")
        table.add_column("Status", style="bold")
        table.add_column("Artifacts", justify="center")

        for e in experiments:
            status_style = "green" if e.status == "completed" else "yellow" if e.status in ["executing", "coding"] else "red"
            artifact_count = len(e.artifacts)
            table.add_row(
                str(e.id),
                e.created_at.strftime("%Y-%m-%d %H:%M"),
                e.topic[:50] + ("..." if len(e.topic) > 50 else ""),
                f"[{status_style}]{e.status.upper()}[/{status_style}]",
                f"{artifact_count} files",
            )

        ui.console.print(table)


@app.command(name="config")
def show_config():
    """
    Inspect the current XavierLabs AI configuration, model routing, and sandbox engine.
    """
    ui.print_banner()
    sandbox, sandbox_desc = get_sandbox()

    from xavierlabs.llm.router import router

    table = Table(title="[bold cyan]XavierLabs AI Configuration & Compute Telemetry[/bold cyan]", show_header=True)
    table.add_column("Component", style="dim", width=25)
    table.add_column("Configured Value", style="white")

    table.add_row("Execution Sandbox", f"[bold green]{sandbox_desc}[/bold green]")
    table.add_row("Active/Auto Model", f"[bold cyan]{router.resolve_auto_model()}[/bold cyan]")
    table.add_row("Ideator Model", settings.IDEATOR_MODEL)
    table.add_row("Reviewer Model", settings.REVIEWER_MODEL)
    table.add_row("Coder Model", settings.CODER_MODEL)
    table.add_row("Synthesizer Model", settings.SYNTHESIZER_MODEL)
    table.add_row("Max Debug Retries", str(settings.MAX_DEBUG_RETRIES))
    table.add_row("Execution Timeout", f"{settings.EXECUTION_TIMEOUT}s")
    table.add_row("Database Engine", f"SQLite ({settings.DB_PATH})")
    table.add_row("Workspace Dir", str(settings.WORKSPACE_DIR.resolve()))

    def get_status(key_val: Optional[str]) -> str:
        return "[green]Detected[/green]" if key_val else "[dim]Not set[/dim]"

    table.add_row("OPENROUTER_API_KEY", get_status(settings.OPENROUTER_API_KEY))
    table.add_row("DEEPSEEK_API_KEY", get_status(settings.DEEPSEEK_API_KEY))
    table.add_row("GROQ_API_KEY", get_status(settings.GROQ_API_KEY))
    table.add_row("OPENAI_API_KEY", get_status(settings.OPENAI_API_KEY))
    table.add_row("ANTHROPIC_API_KEY", get_status(settings.ANTHROPIC_API_KEY))
    table.add_row("GEMINI_API_KEY", get_status(settings.GEMINI_API_KEY))
    if settings.OPENAI_API_BASE:
        table.add_row("OPENAI_API_BASE", f"[green]{settings.OPENAI_API_BASE}[/green]")
    table.add_row("OLLAMA_API_BASE", settings.OLLAMA_API_BASE)

    ui.console.print(table)


@app.command(name="paper")
def build_paper(
    experiment_dir: Path = typer.Argument(..., help="Path to the experiment folder (or topic) to compile paper for"),
    open_viewer: bool = typer.Option(False, "--open", "-o", help="Automatically open the compiled paper in the browser/PDF viewer"),
):
    """
    Compile, inspect, and open the complete research paper (PDF, HTML, and LaTeX) for an experiment.
    """
    import webbrowser
    ui.print_banner()

    exp_path = Path(experiment_dir)
    if not exp_path.exists():
        # Check inside settings.WORKSPACE_DIR
        candidate = settings.WORKSPACE_DIR / experiment_dir
        if candidate.exists():
            exp_path = candidate
        else:
            ui.console.print(f"[bold red]Error:[/bold red] Experiment folder not found: {experiment_dir}")
            raise typer.Exit(code=1)

    pdf_file = exp_path / "paper.pdf"
    html_file = exp_path / "paper.html"
    tex_file = exp_path / "paper.tex"
    md_file = exp_path / "report.md"

    table = Table(title=f"[bold cyan]Research Paper Artifacts ({exp_path.name})[/bold cyan]", show_header=True)
    table.add_column("Format", style="cyan", width=15)
    table.add_column("Status", style="bold", width=15)
    table.add_column("File Path", style="white")

    table.add_row("Publication PDF", "[green]Ready[/green]" if pdf_file.exists() else "[yellow]Missing[/yellow]", str(pdf_file.resolve()))
    table.add_row("Academic HTML", "[green]Ready[/green]" if html_file.exists() else "[yellow]Missing[/yellow]", str(html_file.resolve()))
    table.add_row("LaTeX Source", "[green]Ready[/green]" if tex_file.exists() else "[yellow]Missing[/yellow]", str(tex_file.resolve()))
    table.add_row("Markdown Report", "[green]Ready[/green]" if md_file.exists() else "[yellow]Missing[/yellow]", str(md_file.resolve()))

    ui.console.print(table)

    target_to_open = pdf_file if pdf_file.exists() else html_file if html_file.exists() else md_file
    if open_viewer and target_to_open.exists():
        ui.console.print(f"\n[bold green]Opening {target_to_open.name}...[/bold green]")
        webbrowser.open(target_to_open.as_uri())


if __name__ == "__main__":
    app()
