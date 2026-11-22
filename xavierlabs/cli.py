import os
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.table import Table
from rich.panel import Panel

from xavierlabs.config import settings
from xavierlabs.ui.terminal import (
    ui,
    SYN_FN,
    SYN_STR,
    SYN_VAR,
    SYN_TYPE,
    SYN_NUM,
    SYN_ERR,
    LINE,
    MUTED,
)
from rich import box
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
    """Main callback: starts the interactive chatbot session if no subcommand provided."""
    if ctx.invoked_subcommand is None:
        if not sys.stdin.isatty() and not os.environ.get("XAVIER_FORCE_INTERACTIVE"):
            ui.print_banner()
            ui.console.print("[yellow]Use [bold]xavier --help[/bold] to see available commands.[/yellow]")
            return
        from xavierlabs.ui.chat import ChatSession
        session = ChatSession()
        session.start()


@app.command(name="chat")
def start_chat():
    """
    Launch the interactive conversational scientific research chatbot.
    """
    from xavierlabs.ui.chat import ChatSession
    session = ChatSession()
    session.start()


@app.command(name="research")
def research(
    topic: str = typer.Argument(..., help="Research question, hypothesis, or topic to investigate"),
    codebase: Optional[Path] = typer.Option(None, "--codebase", "-c", help="Path to starting codebase or datasets to ingest"),
    retries: int = typer.Option(settings.MAX_DEBUG_RETRIES, "--retries", "-r", help="Max auto-debugging retries for failing experiments"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override LLM model for all agents (e.g. gemini/gemini-2.5-flash)"),
    force: bool = typer.Option(False, "--force", "-f", help="Run the experiment even if the Reviewer still rejects the hypothesis"),
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

    try:
        orchestrator = ResearchOrchestrator()
        orchestrator.run_research(
            topic=topic,
            starting_code_dir=codebase,
            max_debug_retries=retries,
            proceed_if_rejected=force,
        )
    except Exception as e:
        err_msg = str(e)
        if "No active LLM API key detected" in err_msg or "Missing " in err_msg or "AuthenticationError" in err_msg or "API_KEY" in err_msg:
            ui.console.print(Panel(
                f"[bold red]❌ LLM Provider Authentication Error[/bold red]\n\n"
                f"{err_msg}\n\n"
                f"[bold]How to fix:[/bold]\n"
                f"  • [bold]OpenRouter[/bold]: echo \"OPENROUTER_API_KEY=sk-or-...\" > .env\n"
                f"  • [bold]DeepSeek[/bold]:   echo \"DEEPSEEK_API_KEY=sk-...\" > .env\n"
                f"  • [bold]Ollama[/bold]:     ollama run deepseek-r1 (100% free offline, zero keys needed!)\n"
                f"  • [bold]Google Gemini[/bold]: echo \"GEMINI_API_KEY=AIzaSy...\" > .env\n"
                f"  • [bold]Groq[/bold]:       echo \"GROQ_API_KEY=gsk_...\" > .env\n\n"
                f"Run [bold]xavier config[/bold] to check your current keys.",
                border_style="red"
            ))
            raise typer.Exit(code=1)
        else:
            raise e


@app.command(name="run")
def run_script(
    script_path: Path = typer.Argument(..., help="Path to the Python experiment script to run"),
    timeout: int = typer.Option(settings.EXECUTION_TIMEOUT, "--timeout", "-t", help="Timeout in seconds"),
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

        table = Table(
            title="[bold]Research History[/bold]",
            title_justify="left",
            box=box.SIMPLE_HEAD,
            border_style=LINE,
            header_style=MUTED,
            show_header=True,
            pad_edge=False,
        )
        table.add_column("ID", style=SYN_NUM, width=6)
        table.add_column("Date", style="dim", width=18)
        table.add_column("Topic", style=SYN_STR)
        table.add_column("Status", style="bold")
        table.add_column("Artifacts", justify="center", style=SYN_NUM)

        for e in experiments:
            status_style = SYN_TYPE if e.status == "completed" else SYN_FN if e.status in ["executing", "coding", "rejected"] else SYN_ERR
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

    table = Table(
        title="[bold]Configuration[/bold]",
        title_justify="left",
        box=box.SIMPLE_HEAD,
        border_style=LINE,
        header_style=MUTED,
        show_header=True,
        pad_edge=False,
    )
    table.add_column("Component", style=SYN_VAR, width=25)
    table.add_column("Value", style="")

    table.add_row("Execution Sandbox", f"[{SYN_TYPE}]{sandbox_desc}[/]")
    table.add_row("Active/Auto Model", f"[{SYN_STR}]{router.resolve_auto_model()}[/]")
    table.add_row("Ideator Model", f"[{SYN_STR}]{settings.IDEATOR_MODEL}[/]")
    table.add_row("Reviewer Model", f"[{SYN_STR}]{settings.REVIEWER_MODEL}[/]")
    table.add_row("Coder Model", f"[{SYN_STR}]{settings.CODER_MODEL}[/]")
    table.add_row("Synthesizer Model", f"[{SYN_STR}]{settings.SYNTHESIZER_MODEL}[/]")
    table.add_row("Max Debug Retries", f"[{SYN_NUM}]{settings.MAX_DEBUG_RETRIES}[/]")
    table.add_row("Execution Timeout", f"[{SYN_NUM}]{settings.EXECUTION_TIMEOUT}s[/]")
    table.add_row("Database Engine", f"SQLite ([{SYN_STR}]{settings.DB_PATH}[/])")
    table.add_row("Workspace Dir", f"[{SYN_STR}]{settings.WORKSPACE_DIR.resolve()}[/]")

    def get_status(key_val: Optional[str]) -> str:
        return f"[{SYN_TYPE}]Detected[/]" if key_val else "[dim]Not set[/dim]"

    table.add_row("OPENROUTER_API_KEY", get_status(settings.OPENROUTER_API_KEY))
    table.add_row("DEEPSEEK_API_KEY", get_status(settings.DEEPSEEK_API_KEY))
    table.add_row("GROQ_API_KEY", get_status(settings.GROQ_API_KEY))
    table.add_row("OPENAI_API_KEY", get_status(settings.OPENAI_API_KEY))
    table.add_row("ANTHROPIC_API_KEY", get_status(settings.ANTHROPIC_API_KEY))
    table.add_row("GEMINI_API_KEY", get_status(settings.GEMINI_API_KEY))
    if settings.OPENAI_API_BASE:
        table.add_row("OPENAI_API_BASE", f"[{SYN_STR}]{settings.OPENAI_API_BASE}[/]")
    table.add_row("OLLAMA_API_BASE", f"[{SYN_STR}]{settings.OLLAMA_API_BASE}[/]")

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

    table = Table(
        title=f"[bold]Research Paper Artifacts[/bold] [dim]([/][{SYN_STR}]{exp_path.name}[/][dim])[/]",
        title_justify="left",
        box=box.SIMPLE_HEAD,
        border_style=LINE,
        header_style=MUTED,
        show_header=True,
        pad_edge=False,
    )
    table.add_column("Format", style=SYN_VAR, width=18)
    table.add_column("Status", style="bold", width=12)
    table.add_column("File", style=SYN_STR)

    table.add_row("Publication PDF", f"[{SYN_TYPE}]Ready[/]" if pdf_file.exists() else f"[{SYN_FN}]Missing[/]", str(pdf_file.resolve()))
    table.add_row("Academic HTML", f"[{SYN_TYPE}]Ready[/]" if html_file.exists() else f"[{SYN_FN}]Missing[/]", str(html_file.resolve()))
    table.add_row("LaTeX Source", f"[{SYN_TYPE}]Ready[/]" if tex_file.exists() else f"[{SYN_FN}]Missing[/]", str(tex_file.resolve()))
    table.add_row("Markdown Report", f"[{SYN_TYPE}]Ready[/]" if md_file.exists() else f"[{SYN_FN}]Missing[/]", str(md_file.resolve()))

    ui.console.print(table)

    target_to_open = pdf_file if pdf_file.exists() else html_file if html_file.exists() else md_file
    if open_viewer and target_to_open.exists():
        ui.console.print(f"\n[{SYN_VAR}]Opening[/] [{SYN_STR}]{target_to_open.name}[/]...")
        webbrowser.open(target_to_open.as_uri())


def _save_env_var(key: str, val: str):
    """Safely saves or updates an environment variable in both global and local .env files."""
    paths = [
        Path.home() / ".xavierlabs" / ".env",
        Path(".env"),
    ]
    for p in paths:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            found = False
            if p.exists():
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.strip().startswith(f"{key}=") or line.strip().startswith(f"export {key}="):
                            lines.append(f"{key}={val}\n")
                            found = True
                        else:
                            lines.append(line)
            if not found:
                lines.append(f"{key}={val}\n")
            with open(p, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            pass


@app.command(name="auth")
@app.command(name="setup")
def setup_auth():
    """
    Interactive setup wizard to configure and verify your AI provider keys.
    Saves keys cleanly without quote or encoding issues to ~/.xavierlabs/.env and .env.
    """
    from rich.prompt import Prompt

    ui.print_banner()
    ui.console.print(Panel(
        "[bold]XavierLabs AI Provider Setup Wizard[/bold]\n\n"
        "Configure your API keys effortlessly without messing with .env files or quote formatting.\n"
        "Your keys will be safely stored in [dim]~/.xavierlabs/.env[/dim] so they work across all projects!",
        border_style="grey35"
    ))

    ui.console.print("\n[bold]Select an AI provider to configure:[/bold]")
    ui.console.print("  [1] [bold]Google Gemini[/bold]  (Free tier, fast 1M context - https://aistudio.google.com/app/apikey)")
    ui.console.print("  [2] [bold]OpenRouter[/bold]     (DeepSeek R1, Claude 3.5, Llama 3 - https://openrouter.ai/keys)")
    ui.console.print("  [3] [bold]DeepSeek[/bold]       (Direct DeepSeek API - https://platform.deepseek.com/api_keys)")
    ui.console.print("  [4] [bold]Groq[/bold]           (Ultra-fast Llama 3.3 - https://console.groq.com/keys)")
    ui.console.print("  [5] [bold]OpenAI[/bold]         (GPT-4o, GPT-4o-mini - https://platform.openai.com/api-keys)")
    ui.console.print("  [6] [bold]Anthropic[/bold]      (Claude 3.5 Sonnet/Haiku - https://console.anthropic.com/settings/keys)")
    ui.console.print("  [7] [bold]Local Ollama[/bold]   (100% Free & Offline, NO API keys needed!)")

    choice = Prompt.ask("\nEnter choice [1-7] (or press Enter to cancel)").strip()
    if not choice:
        return

    provider_map = {
        "1": ("GEMINI_API_KEY", "Google Gemini", "gemini/gemini-2.5-flash", "https://aistudio.google.com/app/apikey"),
        "2": ("OPENROUTER_API_KEY", "OpenRouter", "openrouter/deepseek/deepseek-chat", "https://openrouter.ai/keys"),
        "3": ("DEEPSEEK_API_KEY", "DeepSeek", "deepseek/deepseek-chat", "https://platform.deepseek.com/api_keys"),
        "4": ("GROQ_API_KEY", "Groq", "groq/llama-3.3-70b-versatile", "https://console.groq.com/keys"),
        "5": ("OPENAI_API_KEY", "OpenAI", "gpt-4o-mini", "https://platform.openai.com/api-keys"),
        "6": ("ANTHROPIC_API_KEY", "Anthropic", "claude-3-5-haiku-20241022", "https://console.anthropic.com/settings/keys"),
    }

    if choice == "7":
        ui.console.print("\n[bold green]Configuring Local Ollama:[/bold green]")
        ui.console.print("Make sure Ollama is installed and running (https://ollama.com).")
        ui.console.print("Run in a separate terminal: [bold]ollama run deepseek-r1[/bold]")
        _save_env_var("DEFAULT_MODEL", "ollama/deepseek-r1")
        _save_env_var("OLLAMA_API_BASE", "http://localhost:11434")
        ui.console.print("[bold green]✔ Configured default model to 'ollama/deepseek-r1'![/bold green]\n")
        return

    if choice not in provider_map:
        ui.console.print("[red]Invalid choice.[/red]")
        return

    env_var, name, test_model, url = provider_map[choice]
    ui.console.print(f"\n[bold]Get your {name} key at:[/] [dim]{url}[/dim]")
    key_input = Prompt.ask(f"Paste your {env_var}").strip()

    if not key_input:
        ui.console.print("[yellow]Setup cancelled. No key entered.[/yellow]")
        return

    # Clean key string
    clean_key = key_input.strip("'\" \t\r\n")

    # Save to global and local .env
    _save_env_var(env_var, clean_key)
    os.environ[env_var] = clean_key
    if env_var == "GEMINI_API_KEY":
        os.environ["GOOGLE_API_KEY"] = clean_key

    # Live verification ping
    ui.console.print(f"\n[dim]Verifying {name} key with a live test completion ({test_model})...[/dim]")
    try:
        from litellm import completion
        res = completion(
            model=test_model,
            messages=[{"role": "user", "content": "Respond with the single word 'VALID'."}],
            max_tokens=10,
        )
        reply = res.choices[0].message.content.strip()
        ui.console.print(f"[bold green]✔ SUCCESS! Your {name} key is verified and working![/bold green]")
        ui.console.print(f"[dim]Provider response: '{reply}'[/dim]\n")
    except Exception as e:
        ui.console.print(f"[bold red]❌ Key verification failed:[/bold red] {e}\n")
        ui.console.print("[yellow]Double-check that you copied the complete key without missing characters.[/yellow]\n")


if __name__ == "__main__":
    app()
