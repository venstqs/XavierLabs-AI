import os
import sys
from pathlib import Path
from typing import Optional, List
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from xavierlabs.config import settings
from xavierlabs.ui.terminal import ui
from xavierlabs.llm.router import router
from xavierlabs.sandbox.manager import get_sandbox
from xavierlabs.loop.orchestrator import ResearchOrchestrator
from xavierlabs.db.session import init_db, engine
from sqlmodel import Session, select
from xavierlabs.db.models import Experiment


HELP_COMMANDS = [
    ("/research <topic>", "Launch autonomous research loop (literature -> code -> paper)"),
    ("/paper [folder]", "Inspect or open compiled research paper artifacts"),
    ("/history", "Browse and inspect past experiment records"),
    ("/model [name]", "Switch active LLM model or provider on the fly"),
    ("/auth or /setup", "Configure & live-verify your AI provider API keys"),
    ("/config", "View active compute telemetry and detected API keys"),
    ("/clear", "Clear the terminal screen"),
    ("/help", "Show this list of commands"),
    ("/exit or quit", "Exit the interactive session"),
]


class ChatSession:
    """
    Antigravity CLI-style Interactive Chatbot & Scientific Research REPL.
    Allows continuous interaction, conversational hypothesis brainstorming,
    and single-click autonomous experiment execution.
    """

    def __init__(self):
        self.running = True
        self.orchestrator = ResearchOrchestrator()
        self.active_topic: Optional[str] = None

    def start(self):
        """Starts the interactive chatbot REPL."""
        ui.console.clear()
        ui.print_banner()
        self._print_welcome()

        while self.running:
            try:
                prompt_label = "[bold #9ec97b]xavier[/bold #9ec97b]"
                if self.active_topic:
                    prompt_label += f" [dim](research:{self.active_topic[:16]}...)[/dim]"
                prompt_label += " [dim]›[/dim]"

                user_input = Prompt.ask(prompt_label).strip()

                if not user_input:
                    continue

                self.handle_input(user_input)

            except (KeyboardInterrupt, EOFError):
                ui.console.print("\n[dim]Use /exit or quit to leave XavierLabs.[/dim]")
            except Exception as e:
                ui.console.print(f"[bold red]Error:[/bold red] {e}\n")

    def _print_welcome(self):
        sandbox, sandbox_desc = get_sandbox()
        current_model = router.resolve_auto_model()

        status_table = Table.grid(padding=(0, 2))
        status_table.add_column(style="dim")
        status_table.add_column(style="bold white")

        status_table.add_row("Active Model:", f"[cyan]{current_model}[/cyan]")
        status_table.add_row("Execution Sandbox:", f"[green]{sandbox_desc}[/green]")
        status_table.add_row("Workspace Dir:", f"[dim]{settings.WORKSPACE_DIR.resolve()}[/dim]")

        ui.console.print(Panel(
            status_table,
            title="[bold #9ec97b]XavierLabs AI Interactive Console[/bold #9ec97b]",
            subtitle="[dim]Type any topic to research, chat naturally, or type /help for commands[/dim]",
            border_style="#9ec97b",
        ))
        ui.console.print()

    def handle_input(self, text: str):
        # 1. Slash commands
        if text.startswith("/"):
            parts = text[1:].strip().split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ["exit", "quit", "q"]:
                self.cmd_exit()
            elif cmd in ["help", "h", "?"]:
                self.cmd_help()
            elif cmd in ["clear", "cls"]:
                self.cmd_clear()
            elif cmd == "research":
                if not arg:
                    ui.console.print("[yellow]Usage: /research <scientific question or topic>[/yellow]")
                else:
                    self.run_research_workflow(arg)
            elif cmd == "paper":
                self.cmd_paper(arg)
            elif cmd == "history":
                self.cmd_history()
            elif cmd == "model":
                self.cmd_model(arg)
            elif cmd in ["auth", "setup"]:
                from xavierlabs.cli import setup_auth
                setup_auth()
            elif cmd == "config":
                self.cmd_config()
            else:
                ui.console.print(f"[yellow]Unknown command '{text}'. Type /help for available options.[/yellow]")
            return

        # 2. Natural language exit
        if text.lower() in ["exit", "quit", "q"]:
            self.cmd_exit()
            return

        # 3. Direct natural research triggers
        lower = text.lower()
        if lower.startswith("research ") or lower.startswith("investigate ") or lower.startswith("study "):
            topic = text.split(" ", 1)[1].strip()
            self.run_research_workflow(topic)
            return

        # 4. Conversational Assistant Mode (Ideate / Brainstorm)
        self.conversational_assist(text)

    def conversational_assist(self, user_msg: str):
        """Converses with user to explore research ideas before triggering the swarm."""
        ui.console.print("[dim]Thinking...[/dim]")
        system_prompt = (
            "You are XavierLabs AI, an expert scientific research companion. "
            "Help the user explore scientific hypotheses, mathematical formulations, ML experiments, "
            "and computational simulation topics. "
            "Keep answers concise, scientifically rigorous, and focused on testable code/simulations. "
            "Conclude by asking if they would like to run the autonomous research loop on this topic."
        )

        try:
            response = router.generate(
                role="ideator",
                system_prompt=system_prompt,
                user_prompt=user_msg,
                temperature=0.7,
            )
            ui.console.print()
            ui.console.print(Markdown(response))
            ui.console.print()

            # Offer to launch autonomous research
            if Confirm.ask("[bold green]Would you like XavierLabs to launch an autonomous research run on this topic now?[/bold green]", default=True):
                self.run_research_workflow(user_msg)

        except Exception as e:
            err_msg = str(e)
            ui.console.print(f"[bold red]LLM Error:[/bold red] {err_msg}")
            ui.console.print("[dim]Tip: Type /config to inspect your API keys or /model to change providers.[/dim]\n")

    def run_research_workflow(self, topic: str):
        """Executes the end-to-end scientific research loop."""
        ui.console.print(f"\n[bold #9ec97b]▶ Launching Autonomous Research Swarm for:[/] [white]{topic}[/]\n")
        self.active_topic = topic
        try:
            exp_dir = self.orchestrator.run_research(topic=topic)
            ui.console.print(f"\n[bold green]✔ Research run complete![/bold green] Artifacts saved in [cyan]{exp_dir}[/cyan]\n")
            
            # Offer to view paper
            if Confirm.ask("Open compiled research paper in viewer now?", default=True):
                from xavierlabs.cli import build_paper
                build_paper(experiment_dir=exp_dir, open_viewer=True)

        except Exception as e:
            err_msg = str(e)
            ui.console.print(Panel(
                f"[bold red]Research Execution Halted[/bold red]\n\n{err_msg}",
                border_style="red"
            ))
        finally:
            self.active_topic = None

    def cmd_help(self):
        table = Table(title="[bold #9ec97b]XavierLabs AI Interactive Commands[/bold #9ec97b]", show_header=True)
        table.add_column("Command", style="cyan", width=24)
        table.add_column("Description", style="white")

        for cmd, desc in HELP_COMMANDS:
            table.add_row(cmd, desc)

        ui.console.print(table)
        ui.console.print("[dim]You can also type questions or research ideas directly without any prefix![/dim]\n")

    def cmd_clear(self):
        ui.console.clear()
        ui.print_banner()
        self._print_welcome()

    def cmd_model(self, model_name: str):
        if not model_name:
            ui.console.print(f"Current active model: [bold cyan]{router.resolve_auto_model()}[/bold cyan]")
            ui.console.print("\n[dim]Popular choices:[/dim]")
            ui.console.print("  • openrouter/deepseek/deepseek-r1")
            ui.console.print("  • deepseek/deepseek-chat")
            ui.console.print("  • ollama/deepseek-r1  (100% free offline)")
            ui.console.print("  • gemini/gemini-2.5-flash")
            ui.console.print("  • groq/llama-3.3-70b-versatile")
            ui.console.print("  • gpt-4o-mini")
            new_model = Prompt.ask("\nEnter model name or provider (or press Enter to cancel)").strip()
            if new_model:
                model_name = new_model
            else:
                return

        settings.DEFAULT_MODEL = model_name
        settings.IDEATOR_MODEL = model_name
        settings.REVIEWER_MODEL = model_name
        settings.CODER_MODEL = model_name
        settings.SYNTHESIZER_MODEL = model_name
        ui.console.print(f"[bold green]✔ Model updated to:[/] [cyan]{model_name}[/cyan]\n")

    def cmd_config(self):
        from xavierlabs.cli import show_config
        show_config()

    def cmd_history(self):
        from xavierlabs.cli import show_history
        show_history(limit=10)

    def cmd_paper(self, folder: str):
        from xavierlabs.cli import build_paper
        if not folder:
            init_db()
            with Session(engine) as session:
                experiments = session.exec(select(Experiment).order_by(Experiment.created_at.desc()).limit(5)).all()
                if not experiments:
                    ui.console.print("[yellow]No past experiments found.[/yellow]")
                    return

                ui.console.print("\n[bold cyan]Recent Experiments:[/bold cyan]")
                for idx, exp in enumerate(experiments, 1):
                    ui.console.print(f"  [{idx}] [bold]{exp.topic}[/bold] [dim]({exp.workspace_path})[/dim]")

                choice = Prompt.ask("\nEnter number to inspect paper (or Enter to cancel)").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(experiments):
                    selected = experiments[int(choice) - 1]
                    build_paper(experiment_dir=Path(selected.workspace_path), open_viewer=True)
                return

        build_paper(experiment_dir=Path(folder), open_viewer=True)

    def cmd_exit(self):
        ui.console.print("[bold #9ec97b]Exiting XavierLabs AI. Keep exploring![/bold #9ec97b]\n")
        self.running = False
