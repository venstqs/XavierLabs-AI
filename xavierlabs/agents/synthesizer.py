import html
import os
import re
import json
import shutil
import subprocess
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

    def generate_html_paper(
        self,
        hypothesis: HypothesisConfig,
        metrics: Dict[str, Any],
        literature: List[AcademicPaper],
        markdown_body: str,
    ) -> str:
        """Generates a publication-grade standalone HTML paper with MathJax and academic CSS."""
        esc = html.escape
        lit_items = "".join(
            f"<li><strong>{esc(p.title)}</strong> ({p.year or 'N/A'}) - <em>{esc(', '.join(p.authors[:3]))}</em>. "
            f"<a href=\"{esc(p.url, quote=True)}\" target=\"_blank\" rel=\"noopener\">[Link]</a></li>"
            for p in literature
        )

        def fmt_value(v: Any) -> str:
            text = json.dumps(v, default=str) if isinstance(v, (dict, list)) else str(v)
            return esc(text if len(text) <= 300 else text[:300] + "...")

        metrics_rows = "".join(
            f"<tr><td><code>{esc(str(k))}</code></td><td><strong>{fmt_value(v)}</strong></td></tr>"
            for k, v in metrics.items()
        )
        title = esc(hypothesis.title)
        motivation = esc(hypothesis.motivation)
        theory = esc(hypothesis.theoretical_basis)
        design = esc(hypothesis.experimental_design)

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
    @page {{ size: A4; margin: 20mm; }}
    body {{
        font-family: 'Times New Roman', Times, serif;
        line-height: 1.5;
        color: #111;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background: #fff;
    }}
    h1.title {{
        text-align: center;
        font-size: 24pt;
        margin-bottom: 8px;
        font-weight: bold;
    }}
    .authors {{
        text-align: center;
        font-style: italic;
        font-size: 11pt;
        margin-bottom: 24px;
        color: #333;
    }}
    .abstract-box {{
        background: #f9f9f9;
        border-left: 4px solid #282c34;
        padding: 16px 20px;
        margin: 20px 0 30px 0;
        font-size: 10.5pt;
    }}
    .abstract-title {{
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 9pt;
        margin-bottom: 6px;
    }}
    h2 {{
        font-size: 14pt;
        border-bottom: 1.5px solid #222;
        padding-bottom: 4px;
        margin-top: 28px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    h3 {{ font-size: 12pt; margin-top: 18px; }}
    p {{ text-align: justify; font-size: 11pt; margin-bottom: 12px; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 10.5pt;
    }}
    th, td {{
        border: 1px solid #ccc;
        padding: 8px 12px;
        text-align: left;
    }}
    th {{ background: #f0f0f0; }}
    .figure-container {{
        text-align: center;
        margin: 24px 0;
    }}
    .figure-container img {{
        max-width: 100%;
        height: auto;
        border: 1px solid #eee;
        border-radius: 4px;
    }}
    .caption {{
        font-size: 9.5pt;
        color: #555;
        margin-top: 8px;
        font-style: italic;
    }}
    ol.references {{
        font-size: 10pt;
        padding-left: 20px;
    }}
    ol.references li {{ margin-bottom: 6px; }}
</style>
</head>
<body>

<h1 class="title">{title}</h1>
<div class="authors">
    <strong>XavierLabs AI Computational Research Swarm</strong><br>
    Autonomous Terminal-Native Scientific Research Engine
</div>

<div class="abstract-box">
    <div class="abstract-title">Abstract</div>
    <p>{motivation} In this paper, we computationally investigate this hypothesis through empirical simulations and rigorous telemetry analysis. Our results quantify convergence dynamics and parameter sensitivity across standardized benchmarks.</p>
</div>

<h2>1. Introduction & Theoretical Motivation</h2>
<p>{motivation}</p>
<p><strong>Theoretical Formulation:</strong> {theory}</p>

<h2>2. Experimental Methodology</h2>
<p>{design}</p>

<h2>3. Quantitative Findings & Metrics</h2>
<table>
    <thead>
        <tr><th>Metric Name</th><th>Recorded Value</th></tr>
    </thead>
    <tbody>
        {metrics_rows}
    </tbody>
</table>

<div class="figure-container">
    <img src="plot.png" alt="Experimental Visualization" onerror="this.style.display='none'">
    <div class="caption">Figure 1: Telemetry and trajectory visualization generated from empirical metrics.</div>
</div>

<h2>4. Literature & Citations</h2>
<ol class="references">
    {lit_items}
</ol>

</body>
</html>
"""
        return html_doc

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

