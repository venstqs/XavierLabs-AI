import os
import sys
from pathlib import Path
from typing import Optional, List
from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

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
    Interactive Chatbot & Scientific Research REPL.
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
                prompt_label = f"[bold {SYN_FN}]xavier[/]"
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
                ui.console.print(f"[bold {SYN_ERR}]Error:[/] {e}\n")

    def _print_welcome(self):
        sandbox, sandbox_desc = get_sandbox()
        current_model = router.resolve_auto_model()

        status_table = Table.grid(padding=(0, 3))
        status_table.add_column(style=SYN_VAR, no_wrap=True)
        status_table.add_column()

        status_table.add_row("model", f"[{SYN_STR}]{current_model}[/]")
        status_table.add_row("sandbox", f"[{SYN_TYPE}]{sandbox_desc}[/]")
        status_table.add_row("workspace", f"[{MUTED}]{settings.WORKSPACE_DIR.resolve()}[/]")

        ui.console.print(Panel(
            status_table,
            box=box.ROUNDED,
            border_style=LINE,
            padding=(0, 2),
        ))
        ui.console.print(
            f"[{MUTED}]Describe a topic to brainstorm, [/]"
            f"[{SYN_FN}]/research[/] [{SYN_STR}]<topic>[/]"
            f"[{MUTED}] to run the swarm, or [/][{SYN_FN}]/help[/][{MUTED}].[/]\n"
        )

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
                    ui.console.print(f"[{SYN_FN}]Usage: /research <scientific question or topic>[/]")
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
                ui.console.print(f"[{SYN_FN}]Unknown command '{text}'. Type /help for available options.[/]")
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
            if Confirm.ask(f"[bold {SYN_FN}]Launch an autonomous research run on this topic now?[/]", default=True):
                self.run_research_workflow(user_msg)

        except Exception as e:
            err_msg = str(e)
            ui.console.print(f"[bold {SYN_ERR}]LLM Error:[/] {err_msg}")
            ui.console.print("[dim]Tip: Type /config to inspect your API keys or /model to change providers.[/dim]\n")

    def run_research_workflow(self, topic: str):
        """Executes the end-to-end scientific research loop."""
        ui.console.print(f"\n[{SYN_TYPE}]▶[/] [bold white]Launching research swarm:[/bold white] [{SYN_STR}]{topic}[/]\n")
        self.active_topic = topic
        try:
            outcome = self.orchestrator.run_research(topic=topic)
            exp_dir = outcome["workspace"]

            if outcome.get("status") == "rejected":
                return
            if outcome.get("status") != "completed":
                ui.console.print(f"\n[bold {SYN_FN}]Research run did not complete.[/] Partial files are in [{SYN_STR}]{exp_dir}[/]\n")
                return

            ui.console.print(f"\n[bold {SYN_TYPE}]✔ Research run complete![/] Artifacts saved in [{SYN_STR}]{exp_dir}[/]\n")

            # Offer to view paper
            if Confirm.ask("Open compiled research paper in viewer now?", default=True):
                from xavierlabs.cli import build_paper
                build_paper(experiment_dir=exp_dir, open_viewer=True)

        except Exception as e:
            err_msg = str(e)
            ui.console.print(Panel(
                f"[bold {SYN_ERR}]Research Execution Halted[/]\n\n{err_msg}",
                border_style=SYN_ERR
            ))
        finally:
            self.active_topic = None

    def cmd_help(self):
        table = Table(
            title="[bold]Commands[/bold]",
            title_justify="left",
            box=box.SIMPLE_HEAD,
            border_style=LINE,
            header_style=MUTED,
            show_header=True,
            pad_edge=False,
        )
        table.add_column("Command", style=SYN_FN, width=24)
        table.add_column("Description", style="")

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
            ui.console.print(f"Current active model: [bold {SYN_STR}]{router.resolve_auto_model()}[/]")
            ui.console.print("\n[dim]Popular choices:[/dim]")
            ui.console.print(f"  • [{SYN_STR}]openrouter/deepseek/deepseek-r1[/]")
            ui.console.print(f"  • [{SYN_STR}]deepseek/deepseek-chat[/]")
            ui.console.print(f"  • [{SYN_STR}]ollama/deepseek-r1[/]  [dim](100% free offline)[/dim]")
            ui.console.print(f"  • [{SYN_STR}]gemini/gemini-2.5-flash[/]")
            ui.console.print(f"  • [{SYN_STR}]groq/llama-3.3-70b-versatile[/]")
            ui.console.print(f"  • [{SYN_STR}]gpt-4o-mini[/]")
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
        ui.console.print(f"[bold {SYN_TYPE}]✔ Model updated to:[/] [bold {SYN_STR}]{model_name}[/]\n")

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
                    ui.console.print(f"[{SYN_FN}]No past experiments found.[/]")
                    return

                ui.console.print("\n[bold]Recent Experiments:[/bold]")
                for idx, exp in enumerate(experiments, 1):
                    ui.console.print(f"  [[{SYN_NUM}]{idx}[/]] [bold {SYN_STR}]{exp.topic}[/] [dim]({settings.WORKSPACE_DIR / exp.slug})[/dim]")

                choice = Prompt.ask("\nEnter number to inspect paper (or Enter to cancel)").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(experiments):
                    selected = experiments[int(choice) - 1]
                    build_paper(experiment_dir=settings.WORKSPACE_DIR / selected.slug, open_viewer=True)
                return

        build_paper(experiment_dir=Path(folder), open_viewer=True)

    def cmd_exit(self):
        ui.console.print("[bold]Exiting XavierLabs AI. Keep exploring![/bold]\n")
        self.running = False
