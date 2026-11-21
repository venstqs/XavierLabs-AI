import json
import pytest
import os
from pathlib import Path

from xavierlabs.agents.coder import CoderAgent
from xavierlabs.agents.ideator import HypothesisConfig
from xavierlabs.agents.synthesizer import SynthesizerAgent
from xavierlabs.sandbox.local_sandbox import LocalSandbox
from xavierlabs.tools.academic import AcademicPaper


# ---------------------------------------------------------------- sandbox

def test_stale_metrics_are_not_reported(tmp_path: Path):
    """A failing retry must not inherit metrics.json written by an earlier attempt."""
    (tmp_path / "metrics.json").write_text(json.dumps({"accuracy": 0.99}))
    script = tmp_path / "experiment.py"
    script.write_text("raise ValueError('boom')\n")

    result = LocalSandbox().run_script(script, tmp_path, timeout=10)

    assert result.success is False
    assert result.metrics == {}


def test_clear_metrics_false_preserves_file(tmp_path: Path):
    """plot.py runs with clear_metrics=False and must still be able to read metrics.json."""
    (tmp_path / "metrics.json").write_text(json.dumps({"loss": 0.1}))
    script = tmp_path / "plot.py"
    script.write_text("import json; print(json.load(open('metrics.json'))['loss'])\n")

    result = LocalSandbox().run_script(script, tmp_path, timeout=10, clear_metrics=False)

    assert result.success is True
    assert "0.1" in result.stdout


def test_api_keys_not_exposed_to_generated_code(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-should-not-leak")
    monkeypatch.setenv("SOME_SERVICE_TOKEN", "tok-should-not-leak")
    script = tmp_path / "experiment.py"
    script.write_text(
        "import os, json\n"
        "json.dump({'leaked': [k for k in ('OPENAI_API_KEY', 'SOME_SERVICE_TOKEN') if k in os.environ]},"
        " open('metrics.json', 'w'))\n"
    )

    result = LocalSandbox().run_script(script, tmp_path, timeout=10)

    assert result.success is True
    assert result.metrics == {"leaked": []}


# ---------------------------------------------------------------- code extraction

def test_coder_extracts_py_tagged_block():
    text = "Sure:\n```py\nprint('hi')\n```\n"
    assert CoderAgent()._extract_python_code(text) == "print('hi')"


def test_coder_extracts_python3_tagged_block():
    text = "```python3\nimport numpy as np\n```"
    assert CoderAgent()._extract_python_code(text) == "import numpy as np"


def test_synthesizer_extracts_tex_block_without_tag_leak():
    text = "```tex\n\\documentclass{article}\n```"
    assert SynthesizerAgent()._extract_code(text, "latex") == "\\documentclass{article}"


# ---------------------------------------------------------------- HTML paper

def _hypothesis(**overrides) -> HypothesisConfig:
    data = dict(
        title="Bounds where x < y & y > z",
        motivation="Why <script>alert(1)</script> matters",
        theoretical_basis="f(x) = x^2 when a < b",
        parameters={"lr": 0.1},
        metrics=["loss"],
        experimental_design="Run & compare",
        literature_citations=[],
    )
    data.update(overrides)
    return HypothesisConfig(**data)


def test_html_paper_escapes_llm_content():
    paper = AcademicPaper(
        title="A <b>bold</b> claim", authors=["A & B"], abstract="", year=2024,
        url="https://example.org/?a=1&b=2", source="arxiv",
    )
    html_out = SynthesizerAgent().generate_html_paper(
        hypothesis=_hypothesis(),
        metrics={"loss<min>": 0.5, "curve": [1, 2, 3]},
        literature=[paper],
        markdown_body="",
    )

    assert "<script>alert(1)</script>" not in html_out
    assert "&lt;script&gt;" in html_out
    assert "x &lt; y &amp; y &gt; z" in html_out
    assert "loss&lt;min&gt;" in html_out
    assert "A &lt;b&gt;bold&lt;/b&gt; claim" in html_out


def test_html_paper_renders_markdown_report_and_keeps_math():
    report = (
        "# Duplicate Title\n\n## Executive Summary\n\nWe find **strong** effects where "
        "$a_i * b_j$ holds.\n\n| k | v |\n|---|---|\n| loss | 0.1 |\n\n<script>bad()</script>\n"
    )
    out = SynthesizerAgent().generate_html_paper(
        hypothesis=_hypothesis(), metrics={"loss": 0.1}, literature=[], markdown_body=report,
    )
    assert "<h2>Executive Summary</h2>" in out
    assert "<strong>strong</strong>" in out
    assert "$a_i * b_j$" in out          # math untouched by markdown emphasis
    assert "<table>" in out
    assert "<script>bad()</script>" not in out
    assert "Duplicate Title" not in out  # leading H1 dropped; header shows the title


# ---------------------------------------------------------------- config / review

def test_legacy_timeout_env_alias(monkeypatch):
    from xavierlabs.config import Settings
    monkeypatch.delenv("EXECUTION_TIMEOUT", raising=False)
    monkeypatch.setenv("EXPERIMENT_TIMEOUT_SECONDS", "42")
    assert Settings(_env_file=None).EXECUTION_TIMEOUT == 42


def _review_json(overall, feasibility, approved):
    return {"novelty_score": 8, "rigor_score": 8, "feasibility_score": feasibility, "overall_score": overall,
            "approved": approved, "strengths": [], "weaknesses": ["vague"], "modifications_required": "be specific"}


def test_reviewer_enforces_threshold_over_llm_flag(monkeypatch):
    from xavierlabs.agents.reviewer import ReviewerAgent
    agent = ReviewerAgent()
    monkeypatch.setattr(agent.router, "generate_json", lambda **kw: _review_json(5.0, 9.0, True))
    assert agent.review_hypothesis(_hypothesis()).approved is False
    monkeypatch.setattr(agent.router, "generate_json", lambda **kw: _review_json(8.0, 7.0, False))
    assert agent.review_hypothesis(_hypothesis()).approved is True


def test_rejected_hypothesis_stops_before_coding(monkeypatch):
    from xavierlabs.loop.orchestrator import ResearchOrchestrator
    from xavierlabs.config import settings

    orch = ResearchOrchestrator()
    monkeypatch.setattr(settings, "MAX_REFINEMENT_ROUNDS", 2)
    monkeypatch.setattr(orch.ideator, "discover_literature", lambda topic, max_papers=6: [])
    ideas = []
    monkeypatch.setattr(orch.ideator, "formulate_hypothesis", lambda **kw: ideas.append(kw) or _hypothesis())
    monkeypatch.setattr(orch.reviewer.router, "generate_json", lambda **kw: _review_json(4.0, 4.0, False))
    monkeypatch.setattr(orch.coder, "generate_experiment_code", lambda *a, **k: pytest.fail("coder must not run"))

    out = orch.run_research("a vague topic")

    assert out["status"] == "rejected"
    assert len(ideas) == 3  # initial + 2 refinement rounds
    assert "vague" in ideas[-1]["critique_feedback"]
