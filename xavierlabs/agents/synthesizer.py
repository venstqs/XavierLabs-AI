import html
import os
import re
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from xavierlabs.agents.base import BaseAgent
from xavierlabs.agents.ideator import HypothesisConfig
from xavierlabs.tools.academic import AcademicPaper


SYNTHESIZER_SYSTEM_PROMPT = """You are 'The Synthesizer', the scientific manuscript and visualization director in the XavierLabs AI swarm.
Your mission is to translate experimental telemetry, numerical metrics, and academic literature into publication-grade scientific artifacts:
1. High-aesthetic data visualization scripts (`plot.py`) using matplotlib/seaborn.
2. An academic LaTeX manuscript (`paper.tex`) ready for arXiv submission.
3. A comprehensive, beautifully formatted Markdown report (`report.md`).
"""


LOGO_SVG = (
    '<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="currentColor"/>'
    '<g transform="translate(7 7) scale(.65)"><defs><mask id="xl-m"><rect width="40" height="40" fill="#fff"/>'
    '<polygon points="2.4,36 11.6,36 31.41,4 22.21,4" fill="#000"/></mask></defs>'
    '<g transform="translate(6.33 0) skewX(-10)" class="mark-ink">'
    '<polygon points="30.0,36 36.0,36 16.19,4 10.19,4" mask="url(#xl-m)"/>'
    '<polygon points="4.0,36 10.0,36 29.81,4 23.81,4"/>'
    '<rect x="12.076" y="25.8" width="15.848" height="4.0"/></g></g></svg>'
)

PAPER_CSS = """
:root { --bg:#fff; --soft:#f5f5f5; --line:#e7e7e7; --line-2:#d4d4d4; --ink:#0a0a0a; --ink-2:#262626;
        --muted:#616161; --dim:#9a9a9a; --live:#16a34a; color-scheme: light; }
@media screen and (prefers-color-scheme: dark) {
  :root { --bg:#0a0a0a; --soft:#161616; --line:#232323; --line-2:#333; --ink:#f5f5f5; --ink-2:#d9d9d9;
          --muted:#a3a3a3; --dim:#6b6b6b; --live:#4ade80; color-scheme: dark; }
}
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: "Geist", system-ui, -apple-system, "Segoe UI", sans-serif;
       font-size: 15.5px; line-height: 1.7; -webkit-font-smoothing: antialiased; }
.paper { max-width: 760px; margin: 0 auto; padding: 40px clamp(16px, 5vw, 40px) 64px; }
.masthead { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;
            padding-bottom: 18px; border-bottom: 1px solid var(--line); margin-bottom: 48px; }
.brand { display: inline-flex; align-items: center; gap: 10px; font-weight: 600; letter-spacing: -.025em; }
.mark { width: 26px; height: 26px; color: var(--ink); }
.mark-ink { fill: var(--bg); }
.meta { display: inline-flex; align-items: center; gap: 10px; color: var(--muted); font-size: .86rem; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--live);
       box-shadow: 0 0 0 4px color-mix(in srgb, var(--live) 18%, transparent); }
.kicker { color: var(--muted); font-size: .9rem; font-weight: 500; margin: 0 0 10px; }
h1 { font-size: clamp(2rem, 5vw, 2.8rem); line-height: 1.05; letter-spacing: -.05em; font-weight: 600; margin: 0; text-wrap: balance; }
.byline { color: var(--muted); margin: 16px 0 40px; font-size: .95rem; }
.body h2 { font-size: 1.35rem; letter-spacing: -.03em; font-weight: 600; margin: 44px 0 12px; padding-top: 18px; border-top: 1px solid var(--line); }
.body h3 { font-size: 1.08rem; letter-spacing: -.02em; font-weight: 600; margin: 28px 0 8px; }
.body p, .body li { color: var(--ink-2); }
.body a { color: var(--ink); text-underline-offset: 3px; }
.body blockquote { margin: 20px 0; padding: 4px 18px; border-left: 2px solid var(--ink); color: var(--muted); }
code { font-family: "Geist Mono", ui-monospace, monospace; font-size: .86em; background: var(--soft);
       border: 1px solid var(--line); border-radius: 6px; padding: .1em .4em; }
pre { background: var(--soft); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; overflow-x: auto; }
pre code { background: none; border: 0; padding: 0; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: .92rem; display: block; overflow-x: auto; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-weight: 600; color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; border-bottom-color: var(--line-2); }
table.metrics td:last-child { font-family: "Geist Mono", ui-monospace, monospace; word-break: break-word; }
img { max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 12px; background: #fff; }
figure { margin: 28px 0; text-align: center; }
figcaption { color: var(--muted); font-size: .86rem; margin-top: 10px; }
.refs li { margin-bottom: 8px; font-size: .92rem; word-break: break-word; }
.foot { margin-top: 64px; padding-top: 18px; border-top: 1px solid var(--line); color: var(--dim); font-size: .82rem; }
@media print { .paper { max-width: none; padding: 0; } .body h2 { break-after: avoid; } figure, table { break-inside: avoid; } }
"""


class SynthesizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="The Synthesizer", role="synthesizer")

    def generate_plot_script(self, metrics: Dict[str, Any], hypothesis: HypothesisConfig) -> str:
        """Generates plot.py using matplotlib/seaborn to visualize metrics."""
        user_prompt = f"""Generate a publication-quality data visualization script (`plot.py`) using matplotlib and seaborn.

Hypothesis:
{hypothesis.title}

Recorded Metrics (from metrics.json):
```json
{json.dumps(metrics, indent=2)}
```

Requirements:
1. Read 'metrics.json' from current working directory.
2. Use seaborn style, publication-quality fonts, distinct colors, and clear legends/labels.
3. If curves/trajectories are present (e.g. loss over epochs, convergence steps), plot them.
4. If summary scalar comparisons exist (e.g. baseline vs proposed), plot bar charts with error bars or comparative figures.
5. Save the output figure to 'plot.png' with dpi=300 and bbox_inches='tight'.
6. Do NOT call plt.show() (headless terminal environment). Use plt.savefig('plot.png').
7. Return only valid Python code wrapped in ```python ... ```.
"""

        response = self.router.generate(
            role=self.role,
            system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        return self._extract_code(response, "python")

    def generate_latex_paper(
        self,
        hypothesis: HypothesisConfig,
        metrics: Dict[str, Any],
        literature: List[AcademicPaper],
        code_script: str,
    ) -> str:
        """Generates an academic-grade LaTeX manuscript paper.tex."""
        lit_context = "\n".join([f"- {p.title} ({p.year or 'N/A'}). {p.url}" for p in literature])

        user_prompt = f"""Write an academic research paper in LaTeX for the following completed computational experiment:

Title: {hypothesis.title}

Theoretical Basis & Motivation:
{hypothesis.motivation}
{hypothesis.theoretical_basis}

Experimental Design:
{hypothesis.experimental_design}

Recorded Numerical Metrics:
{json.dumps(metrics, indent=2)}

Related Literature:
{lit_context}

Requirements:
1. Use standard LaTeX document class: \\documentclass[11pt,a4paper]{{article}}
2. Packages: amsmath, amssymb, graphicx, booktabs, hyperref, geometry, microtype.
3. Include sections:
   - \\title, \\author{{XavierLabs AI Computational Research Swarm}}, \\maketitle
   - Abstract
   - 1. Introduction & Theoretical Motivation
   - 2. Computational Methodology & Experimental Design
   - 3. Empirical Results & Analysis (include a figure referencing plot.png and summary table of metrics)
   - 4. Discussion, Ablation & Limitations
   - 5. Conclusion & Future Directions
   - References / Bibliography
4. Ensure valid LaTeX syntax with no unescaped special characters.
5. Return the raw LaTeX document wrapped in ```latex ... ```.
"""

        response = self.router.generate(
            role=self.role,
            system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4096,
        )

        return self._extract_code(response, "latex")

    def generate_markdown_report(
        self,
        hypothesis: HypothesisConfig,
        metrics: Dict[str, Any],
        literature: List[AcademicPaper],
    ) -> str:
        """Generates a clean, comprehensive Markdown report report.md."""
        lit_context = "\n".join([f"- **{p.title}** ({p.year or 'N/A'}) - [Link]({p.url})" for p in literature])

        user_prompt = f"""Generate an academic-style Markdown research report for the following completed experiment:

Title: {hypothesis.title}

Theoretical Basis & Motivation:
{hypothesis.motivation}
{hypothesis.theoretical_basis}

Experimental Design:
{hypothesis.experimental_design}

Quantitative Metrics:
{json.dumps(metrics, indent=2)}

Related Literature:
{lit_context}

Requirements:
1. Beautiful Markdown hierarchy (# Title, ## Executive Summary, ## Theoretical Foundation, ## Experimental Methodology, ## Quantitative Findings & Analysis, ## Key Takeaways & Limitations, ## References).
2. Render tables for numerical metrics.
3. Reference `![Experiment Plot](plot.png)`.
4. Provide thorough, scientifically rigorous analysis of why the results occurred.
"""

        response = self.router.generate(
            role=self.role,
            system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4096,
        )

        text = response.strip()
        fenced = re.fullmatch(r"```(?:markdown|md)?[ \t]*\n([\s\S]*?)\n?```", text)
        return fenced.group(1).strip() if fenced else text

    @staticmethod
    def _render_markdown(markdown_text: str) -> str:
        """
        Renders Markdown to HTML with raw HTML disabled (so LLM output cannot inject markup).
        TeX math ($...$ and $$...$$) is shielded from Markdown so MathJax can typeset it.
        """
        from markdown_it import MarkdownIt

        math_spans: List[str] = []

        def stash(match: "re.Match[str]") -> str:
            math_spans.append(match.group(0))
            return f"XLMATH{len(math_spans) - 1}XL"

        shielded = re.sub(r"\$\$[\s\S]+?\$\$|(?<![\\$])\$(?!\s)[^$\n]+?(?<!\s)\$", stash, markdown_text)
        md = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table").enable("strikethrough")
        rendered = md.render(shielded)
        return re.sub(r"XLMATH(\d+)XL", lambda m: html.escape(math_spans[int(m.group(1))]), rendered)

    def generate_html_paper(
        self,
        hypothesis: HypothesisConfig,
        metrics: Dict[str, Any],
        literature: List[AcademicPaper],
        markdown_body: str,
    ) -> str:
        """
        Builds a standalone HTML paper from the Markdown report (MathJax enabled),
        styled to the XavierLabs brand, plus a metrics appendix.
        """
        esc = html.escape
        body_md = (markdown_body or "").strip()
        # The page header already shows the title; drop a leading "# Title" line from the report.
        body_md = re.sub(r"\A#\s+[^\n]*\n+", "", body_md)
        if body_md:
            body_html = self._render_markdown(body_md)
        else:
            body_html = (
                f"<h2>Motivation</h2><p>{esc(hypothesis.motivation)}</p>"
                f"<h2>Theoretical Basis</h2><p>{esc(hypothesis.theoretical_basis)}</p>"
                f"<h2>Experimental Design</h2><p>{esc(hypothesis.experimental_design)}</p>"
            )

        figure_html = ""
        if "plot.png" not in body_md:
            figure_html = (
                '<figure><img src="plot.png" alt="Experiment figure" onerror="this.parentElement.remove()">'
                "<figcaption>Figure 1. Visualization generated from the recorded metrics.</figcaption></figure>"
            )

        def fmt_value(v: Any) -> str:
            text = json.dumps(v, default=str) if isinstance(v, (dict, list)) else str(v)
            return esc(text if len(text) <= 300 else text[:300] + "...")

        metrics_rows = "".join(
            f"<tr><td><code>{esc(str(k))}</code></td><td>{fmt_value(v)}</td></tr>"
            for k, v in metrics.items()
        )

        refs_html = ""
        has_refs_section = re.search(r"^#{1,3}\s*(references|bibliography)", body_md, re.IGNORECASE | re.MULTILINE)
        if literature and not has_refs_section:
            items = "".join(
                f"<li>{esc(', '.join(p.authors[:3]))}{' et al.' if len(p.authors) > 3 else ''}. "
                f"<em>{esc(p.title)}</em> ({p.year or 'n.d.'}). "
                f"<a href=\"{esc(p.url, quote=True)}\" target=\"_blank\" rel=\"noopener\">{esc(p.url)}</a></li>"
                for p in literature
            )
            refs_html = f'<h2>References</h2><ol class="refs">{items}</ol>'

        title = esc(hypothesis.title)
        today = datetime.now().strftime("%B %d, %Y")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300..800&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>window.MathJax = {{ tex: {{ inlineMath: [['$', '$']] }} }};</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js" async></script>
<style>
{PAPER_CSS}
</style>
</head>
<body>
<main class="paper">
  <header class="masthead">
    <div class="brand">{LOGO_SVG}<span>XavierLabs</span></div>
    <div class="meta"><span class="dot"></span>Autonomous research report · {today}</div>
  </header>

  <p class="kicker">Computational Research Paper</p>
  <h1>{title}</h1>
  <p class="byline">XavierLabs AI Research Swarm · Ideator · Reviewer · Coder · Synthesizer</p>

  <article class="body">
    {body_html}
    {figure_html}
    <h2>Appendix A. Recorded Metrics</h2>
    <table class="metrics"><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>{metrics_rows}</tbody></table>
    {refs_html}
  </article>

  <footer class="foot">Generated by XavierLabs AI from code executed in a sandbox. Verify results before citing.</footer>
</main>
</body>
</html>
"""

    @staticmethod
    def _find_headless_browser() -> Optional[str]:
        """Locates a Chromium-based browser (Edge, Chrome, Chromium) for HTML-to-PDF printing."""
        candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "chrome"):
            found = shutil.which(name)
            if found:
                return found
        return None

    def compile_pdf(self, html_path: Path, output_pdf_path: Path) -> bool:
        """
        Compiles the HTML paper to PDF using a headless Chromium-based browser (Edge, Chrome or Chromium).
        """
        browser = self._find_headless_browser()
        if not browser:
            return False

        try:
            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                "--virtual-time-budget=10000",  # let MathJax finish rendering before printing
                f"--print-to-pdf={output_pdf_path.resolve()}",
                html_path.resolve().as_uri(),
            ]
            subprocess.run(cmd, capture_output=True, timeout=60)
            return output_pdf_path.exists()
        except Exception:
            return False

    def _extract_code(self, text: str, lang: str = "python") -> str:
        # Prefer a block tagged with the requested language, then any fenced block.
        match = re.search(rf"```{re.escape(lang)}[^\n]*\n([\s\S]*?)```", text, re.IGNORECASE)
        if not match:
            match = re.search(r"```[^\n]*\n([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()
        return text.strip()

