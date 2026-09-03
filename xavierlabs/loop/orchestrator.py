import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from sqlmodel import Session
from xavierlabs.config import settings
from xavierlabs.db.session import engine, init_db
from xavierlabs.db.models import Experiment, HypothesisRecord, RunRecord, ArtifactRecord
from xavierlabs.agents.ideator import IdeatorAgent, HypothesisConfig
from xavierlabs.agents.reviewer import ReviewerAgent, HypothesisReview, CodeAudit
from xavierlabs.agents.coder import CoderAgent
from xavierlabs.agents.synthesizer import SynthesizerAgent
from xavierlabs.sandbox.manager import get_sandbox
from xavierlabs.sandbox.base import ExecutionResult
from xavierlabs.tools.files import WorkspaceInspector
from xavierlabs.ui.terminal import ui


class ResearchOrchestrator:
    """
    Continuous, stateful multi-agent orchestration pipeline
    executing the computational scientific method end-to-end.
    """

    def __init__(self):
        init_db()
        self.ideator = IdeatorAgent()
        self.reviewer = ReviewerAgent()
        self.coder = CoderAgent()
        self.synthesizer = SynthesizerAgent()

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-")[:40]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{slug}_{timestamp}"

    def run_research(
        self,
        topic: str,
        starting_code_dir: Optional[Path] = None,
        max_debug_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        retries = max_debug_retries or settings.MAX_DEBUG_RETRIES
        slug = self._slugify(topic)
        workspace = settings.WORKSPACE_DIR / slug
        workspace.mkdir(parents=True, exist_ok=True)

        ui.print_banner()
        ui.console.print(f"[bold cyan]Initiating Research Run:[/bold cyan] {topic}")
        ui.console.print(f"[dim]Workspace Directory: {workspace.resolve()}[/dim]\n")

        sandbox, sandbox_desc = get_sandbox()
        ui.console.print(f"[bold green]Execution Sandbox:[/bold green] {sandbox_desc}\n")

        with Session(engine) as db_session:
            exp = Experiment(slug=slug, topic=topic, status="ideating")
            db_session.add(exp)
            db_session.commit()
            db_session.refresh(exp)

            # Ingest starting context if available
            workspace_context = ""
            if starting_code_dir and Path(starting_code_dir).exists():
                inspector = WorkspaceInspector(Path(starting_code_dir))
                workspace_context = inspector.read_code_summary()
                ui.console.print(f"[dim]Ingested starting codebase from {starting_code_dir}[/dim]")

            # -------------------------------------------------------------
            # PHASE 1: Discovery & Hypothesis Formulation (Ideator)
            # -------------------------------------------------------------
            ui.print_agent_header(self.ideator.name, self.ideator.role, "Querying literature & formulating hypothesis...")
            with ui.console.status("[cyan]Searching ArXiv & Semantic Scholar...[/cyan]"):
                literature = self.ideator.discover_literature(topic, max_papers=6)

            ui.console.print(f"[green]Retrieved {len(literature)} relevant academic publications.[/green]")
            for p in literature:
                ui.console.print(f"  • [bold]{p.title}[/bold] ({p.year or 'N/A'}) - [dim]{p.url}[/dim]")

            with ui.console.status("[cyan]Formulating mathematical & empirical hypothesis...[/cyan]"):
                hypothesis = self.ideator.formulate_hypothesis(
                    topic=topic,
                    literature=literature,
                    workspace_context=workspace_context,
                )

            ui.print_hypothesis(hypothesis)

            # -------------------------------------------------------------
            # PHASE 2: Peer Review & Critique (Reviewer)
            # -------------------------------------------------------------
            ui.print_agent_header(self.reviewer.name, self.reviewer.role, "Conducting rigorous peer review...")
            with ui.console.status("[yellow]Auditing hypothesis novelty, rigor, and feasibility...[/yellow]"):
                review = self.reviewer.review_hypothesis(hypothesis)

            ui.print_review(review)

            # Refinement loop if rejected
            if not review.approved:
                ui.console.print("[yellow]Hypothesis score below threshold. Ideator refining with Reviewer feedback...[/yellow]")
                with ui.console.status("[cyan]Refining hypothesis...[/cyan]"):
                    hypothesis = self.ideator.formulate_hypothesis(
                        topic=topic,
                        literature=literature,
                        workspace_context=workspace_context,
                        critique_feedback=review.modifications_required,
                    )
                ui.print_hypothesis(hypothesis)
                with ui.console.status("[yellow]Re-evaluating revised hypothesis...[/yellow]"):
                    review = self.reviewer.review_hypothesis(hypothesis)
                ui.print_review(review)

            # Record hypothesis in DB
            hyp_record = HypothesisRecord(
                experiment_id=exp.id,
                title=hypothesis.title,
                motivation=hypothesis.motivation,
                theoretical_basis=hypothesis.theoretical_basis,
                parameters_json=str(hypothesis.parameters),
                metrics_json=str(hypothesis.metrics),
                is_approved=review.approved,
                review_score=review.overall_score,
                review_feedback=review.modifications_required,
            )
            db_session.add(hyp_record)
            exp.status = "coding"
            db_session.commit()

            # -------------------------------------------------------------
            # PHASE 3: Code Generation & Pre-flight Audit (Coder & Reviewer)
            # -------------------------------------------------------------
            ui.print_agent_header(self.coder.name, self.coder.role, "Synthesizing computational experiment (experiment.py)...")
            with ui.console.status("[green]Generating experiment.py...[/green]"):
                script_code = self.coder.generate_experiment_code(hypothesis)

            ui.print_agent_header(self.reviewer.name, self.reviewer.role, "Performing pre-flight safety & reproducibility audit...")
            with ui.console.status("[yellow]Auditing code for seed stability and metric logging...[/yellow]"):
                code_audit = self.reviewer.audit_code(script_code, hypothesis)

            if not code_audit.approved:
                ui.console.print(f"[yellow]Reviewer flagged potential code risks: {code_audit.audit_notes}[/yellow]")
                with ui.console.status("[green]Refining experiment code...[/green]"):
                    script_code = self.coder.generate_experiment_code(
                        hypothesis, audit_feedback=code_audit.audit_notes
                    )

            script_file = workspace / "experiment.py"
            script_file.write_text(script_code, encoding="utf-8")
            ui.console.print(f"[green]Saved {script_file.name} to workspace.[/green]")

            # -------------------------------------------------------------
            # PHASE 4: Sandboxed Execution & Auto-Debugging Loop
            # -------------------------------------------------------------
            exp.status = "executing"
            db_session.commit()

            current_code = script_code
            execution_success = False
            last_result: Optional[ExecutionResult] = None

            for attempt in range(1, retries + 2):
                ui.print_agent_header(
                    "Execution Sandbox",
                    "system",
                    f"Executing experiment in isolated sandbox (Attempt #{attempt})...",
                )
                with ui.console.status(f"[bold green]Running experiment.py (Attempt {attempt})...[/bold green]"):
                    result = sandbox.run_script(script_file, workspace)

                ui.print_execution_telemetry(result, attempt)

                # Record run in DB
                run_rec = RunRecord(
                    experiment_id=exp.id,
                    iteration=attempt,
                    script_content=current_code,
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=result.execution_time,
                    metrics_json=str(result.metrics),
                    success=result.success,
                )
                db_session.add(run_rec)
                db_session.commit()

                if result.success:
                    execution_success = True
                    last_result = result
                    ui.console.print("[bold green]✔ Experiment executed successfully and recorded metrics![/bold green]\n")
                    break

                # If failed and retries remain, invoke auto-debugger
                if attempt <= retries:
                    ui.print_agent_header(
                        self.coder.name,
                        "coder",
                        f"[bold red]AUTONOMOUS DEBUGGING ACTIVATED[/bold red] - Analyzing traceback and fixing experiment.py...",
                    )
                    with ui.console.status("[bold magenta]Coder repairing code from stderr traceback...[/bold magenta]"):
                        current_code = self.coder.debug_experiment_code(
                            failing_code=current_code,
                            stderr_traceback=result.error_traceback or result.stderr,
                            stdout_output=result.stdout,
                            hypothesis=hypothesis,
                        )
                    script_file.write_text(current_code, encoding="utf-8")
                    ui.console.print(f"[green]Patched experiment.py saved. Retrying execution...[/green]")
                else:
                    last_result = result

            if not execution_success:
                exp.status = "failed"
                db_session.commit()
                ui.console.print("[bold red]❌ Experiment failed after max debugging retries.[/bold red]")
                return {"status": "failed", "workspace": str(workspace)}

            # -------------------------------------------------------------
            # PHASE 5: Synthesis & Scientific Artifact Generation
            # -------------------------------------------------------------
            exp.status = "synthesizing"
            db_session.commit()

            ui.print_agent_header(self.synthesizer.name, self.synthesizer.role, "Synthesizing figures, LaTeX paper, and research report...")

            # 1. Visualization (plot.py)
            with ui.console.status("[magenta]Generating publication-grade visualization script (plot.py)...[/magenta]"):
                plot_code = self.synthesizer.generate_plot_script(last_result.metrics, hypothesis)
                plot_file = workspace / "plot.py"
                plot_file.write_text(plot_code, encoding="utf-8")

            with ui.console.status("[magenta]Executing plot.py to render publication figure...[/magenta]"):
                plot_run = sandbox.run_script(plot_file, workspace)

            plot_png = workspace / "plot.png"
            if plot_png.exists():
                ui.console.print("[green]✔ Rendered plot.png successfully![/green]")

            # 2. LaTeX Manuscript (paper.tex)
            with ui.console.status("[magenta]Drafting formal academic manuscript (paper.tex)...[/magenta]"):
                latex_content = self.synthesizer.generate_latex_paper(
                    hypothesis=hypothesis,
                    metrics=last_result.metrics,
                    literature=literature,
                    code_script=current_code,
                )
                latex_file = workspace / "paper.tex"
                latex_file.write_text(latex_content, encoding="utf-8")
                ui.console.print("[green]✔ Generated academic LaTeX paper (paper.tex).[/green]")

            # 3. Markdown Report (report.md)
            with ui.console.status("[magenta]Compiling comprehensive Markdown report (report.md)...[/magenta]"):
                md_content = self.synthesizer.generate_markdown_report(
                    hypothesis=hypothesis,
                    metrics=last_result.metrics,
                    literature=literature,
                )
                md_file = workspace / "report.md"
                md_file.write_text(md_content, encoding="utf-8")
                ui.console.print("[green]✔ Generated comprehensive Markdown report (report.md).[/green]")

            # 4. Standalone Academic HTML & PDF Compilation
            with ui.console.status("[magenta]Compiling publication-grade academic paper (HTML & PDF)...[/magenta]"):
                html_content = self.synthesizer.generate_html_paper(
                    hypothesis=hypothesis,
                    metrics=last_result.metrics,
                    literature=literature,
                    markdown_body=md_content,
                )
                html_file = workspace / "paper.html"
                html_file.write_text(html_content, encoding="utf-8")

                pdf_file = workspace / "paper.pdf"
                pdf_compiled = self.synthesizer.compile_pdf(html_file, pdf_file)
                if not pdf_compiled and shutil.which("pdflatex"):
                    try:
                        subprocess.run(
                            ["pdflatex", "-interaction=nonstopmode", "paper.tex"],
                            cwd=str(workspace),
                            capture_output=True,
                            timeout=60,
                        )
                    except Exception:
                        pass

                if pdf_file.exists():
                    ui.console.print("[bold green]✔ Compiled publication-grade PDF: paper.pdf[/bold green]")

            # Store artifacts in DB
            artifacts_dict = {
                "Executable Script": str(script_file.resolve()),
                "Recorded Metrics": str((workspace / "metrics.json").resolve()),
                "Visualization Code": str(plot_file.resolve()),
                "Publication Figure": str(plot_png.resolve()) if plot_png.exists() else "N/A",
                "LaTeX Manuscript": str(latex_file.resolve()),
                "HTML Paper": str(html_file.resolve()),
                "Academic Report": str(md_file.resolve()),
            }
            if pdf_file.exists():
                artifacts_dict["Publication PDF"] = str(pdf_file.resolve())

            for atype, apath in artifacts_dict.items():
                art_record = ArtifactRecord(
                    experiment_id=exp.id,
                    artifact_type=atype,
                    file_path=apath,
                )
                db_session.add(art_record)

            exp.status = "completed"
            db_session.commit()

            ui.console.print("\n")
            ui.print_artifacts_summary(artifacts_dict)

            ui.console.print("\n[bold cyan]─── EXECUTIVE SUMMARY & FINDINGS ───[/bold cyan]\n")
            ui.print_markdown(md_content[:2500] + ("\n\n*(Full report saved to report.md)*" if len(md_content) > 2500 else ""))

            return {
                "status": "completed",
                "workspace": str(workspace),
                "artifacts": artifacts_dict,
                "metrics": last_result.metrics,
            }
