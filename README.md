<div align="center">

<p align="center">
  <img src="docs/assets/banner.svg" alt="xavierlabs" width="700" />
</p>

### **Autonomous, Terminal-Native Computational Scientific Research Swarm**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![ArXiv Ready](https://img.shields.io/badge/ArXiv-LaTeX%20%26%20PDF-red.svg?style=flat-square&logo=arxiv)](https://arxiv.org/)
[![Multi-Agent Swarm](https://img.shields.io/badge/Architecture-4--Agent%20Swarm-purple.svg?style=flat-square)](https://github.com/venstqs/XavierLabs-AI)
[![Sandbox](https://img.shields.io/badge/Execution-Docker%20%2F%20Subprocess%20Sandbox-yellow.svg?style=flat-square&logo=docker)](https://github.com/venstqs/XavierLabs-AI)
[![LLM Router](https://img.shields.io/badge/LLM-Groq%20%7C%20DeepSeek%20%7C%20Ollama%20%7C%20OpenRouter-orange.svg?style=flat-square)](https://github.com/venstqs/XavierLabs-AI)

[**Live Interactive Demo**](https://venstqs.github.io/XavierLabs-AI/) · [**Technical Documentation**](#system-architecture) · [**Quickstart**](#quickstart) · [**Interactive Chat Mode**](#interactive-chatbot-mode)

---

</div>

## Overview

Traditional computational science requires months of manual labor: reviewing literature, mathematically formulating a hypothesis, writing simulation code from scratch, debugging runtimes, plotting charts, and typesetting LaTeX papers.

**XavierLabs AI** automates the computational scientific method end-to-end. Powered by an autonomous swarm of four specialized AI agents, XavierLabs executes entire research loops—from initial inquiry to compiled arXiv-ready PDF papers—in under three minutes.

Unlike general-purpose LLMs that hallucinate scientific claims, **XavierLabs writes and executes real, reproducible Python code in a contained sandbox**, gathers empirical metrics, and synthesizes formal publications backed by computed mathematical evidence.

---

## System Architecture


```
                         ┌──────────────────────────────┐
                         │   User / Research Inquiry    │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                       ┌────────────────────────────────────┐
                       │     Agent 1: The Ideator           │
                       │  • Queries ArXiv & Semantic Scholar│
                       │  • Formulates testable hypotheses  │
                       │  • Emits strict JSON schemas       │
                       └─────────────────┬──────────────────┘
                                        │
                                        ▼
                       ┌────────────────────────────────────┐
                       │    Agent 2: The Reviewer           │
                       │  • Adversarial peer review         │
                       │  • Audits mathematical rigor (1-10)│
                       │  • Enforces boundary constraints   │
                       └─────────────────┬──────────────────┘
                                        │
                           [Approved]   ▼
                       ┌────────────────────────────────────┐
                       │      Agent 3: The Coder            │
                       │  • Generates experiment.py         │
                       │  • Fixes seeds for reproducibility │
                       │  • Emits numerical metrics.json    │
                       └─────────────────┬──────────────────┘
                                        │
                                        ▼
                       ┌────────────────────────────────────┐
  ◄─────────────────── │   Sandboxed Execution Runtime      │
  │ Auto-Debugging     │  • Docker or Isolated Subprocess   │
  │ Feedback Loop      │  • Captures stdout / stderr traces │
  └─────────────────── └─────────────────┬──────────────────┘
                           [Success]    │
                                        ▼
                       ┌────────────────────────────────────┐
                       │    Agent 4: The Synthesizer        │
                       │  • Renders 300-DPI Seaborn figures │
                       │  • Compiles LaTeX & arXiv PDF      │
                       │  • Authors comprehensive report.md │
                       └────────────────────────────────────┘
```

### The 4 Autonomous Agents

| Agent | Persona | Primary Responsibilities | Artifacts Produced |
| :--- | :--- | :--- | :--- |
| **The Ideator** | Principal Investigator | Literature discovery, gap analysis, theoretical hypothesis formulation. | `hypothesis.json`, ArXiv query references |
| **The Reviewer** | Senior Peer Reviewer | Mathematical critique, physical sanity check, experimental parameter validation. | Review Score (1–10), audit feedback |
| **The Coder** | Simulation Engineer | Self-contained Python simulation scripts (`numpy`, `scipy`, `torch`), auto-debugging. | `experiment.py`, `metrics.json`, debug logs |
| **The Synthesizer** | Publication Director | Data visualization scripts, LaTeX manuscript authoring, academic report compilation. | `plot.py`, `plot.png`, `paper.tex`, `paper.pdf` |

---

## Key Capabilities

### 1. Dual Sandbox Execution & Self-Healing Auto-Debugger
- **Isolated Containment**: Simulations run in an ephemeral Docker container or an isolated local subprocess sandbox with wall-clock timeouts and memory limits.
- **Self-Healing Debugger**: If a script crashes (e.g. dimension mismatch, singular matrix, or import failure), the system intercepts the stderr traceback, passes it back to The Coder, and autonomously rewrites and re-executes the code.

### 2. Universal Model Router (LiteLLM)
Works with **ANY** state-of-the-art model or 100% offline local models:
- **Groq**: Sub-second inference with built-in sliding-window rate limit recovery.
- **DeepSeek Direct**: `deepseek-chat` and `deepseek-reasoner` (R1) for mathematical rigor.
- **OpenRouter**: Access 100+ models (Claude 3.5 Sonnet, Llama 3.3, Qwen 2.5) with a single API key.
- **Local Ollama**: 100% private, free, and offline (`ollama run deepseek-r1`).
- **Frontier Providers**: Google Gemini, OpenAI (GPT-4o), Anthropic Claude.

### 3. Publication-Grade Academic Synthesis
- **Formal LaTeX Manuscripts**: Automatically produces `paper.tex` with standard academic document classes (`amsmath`, `booktabs`, `graphicx`, `hyperref`).
- **Vector / High-DPI Visualizations**: Generates `plot.png` (300 DPI) using Seaborn styles.
- **Compiled PDFs**: One-click compilation of camera-ready arXiv PDFs.

### 4. Persistent Experiment Telemetry (SQLite)
Every research run, hypothesis configuration, simulation code iteration, and compiled artifact is persisted into a local SQLite database (`xavierlabs.db`) for full auditability.

---

## Quickstart

### Installation

```bash
# Option 1: Direct pip install from GitHub
pip install git+https://github.com/venstqs/XavierLabs-AI.git

# Option 2: Using uv (fastest)
uv pip install git+https://github.com/venstqs/XavierLabs-AI.git

# Option 3: Developer editable clone
git clone https://github.com/venstqs/XavierLabs-AI.git
cd XavierLabs-AI
pip install -e .
```

### Configuration (`.env`)

Create a `.env` file in your workspace or home directory:

```bash
# Option A: Groq (Ultra-fast free inference - Recommended)
GROQ_API_KEY=gsk_...

# Option B: OpenRouter (Access all frontier models)
OPENROUTER_API_KEY=sk-or-v1-...

# Option C: DeepSeek Direct
DEEPSEEK_API_KEY=sk-...

# Option D: 100% Offline with Ollama (Zero API keys required!)
# DEFAULT_MODEL=ollama/deepseek-r1
```

---

## CLI Usage

### Interactive Chatbot Mode
Launch XavierLabs in an interactive, Antigravity CLI-style conversational session:

```bash
xavier
```

In interactive mode, you can chat conversationally about research ideas, refine experimental parameters, and trigger autonomous runs seamlessly:

```text
xavier [ready] › /help
┌────────────────────────┬─────────────────────────────────────────────────┐
│ Command                │ Description                                     │
├────────────────────────┼─────────────────────────────────────────────────┤
│ /research <topic>      │ Launch autonomous research loop                 │
│ /paper [folder]        │ Inspect or open compiled research paper         │
│ /history               │ Browse and inspect past experiment records      │
│ /model [name]          │ Switch model (Groq, DeepSeek, Ollama, etc.)     │
│ /config                │ View compute telemetry & detected API keys      │
│ /exit                  │ Exit interactive session                        │
└────────────────────────┴─────────────────────────────────────────────────┘

xavier [ready] › I want to test AdamW vs Lion optimizer on non-convex loss
● THE IDEATOR Analyzing hypothesis novelty and testable metrics...
  • Proposed hypothesis: Lion yields 1.48x convergence acceleration over AdamW.

Would you like XavierLabs to launch an autonomous research run on this topic now? [Y/n]: y
▶ Launching Autonomous Research Swarm...
```

---

### Direct Autonomous Research (One-Liner)

```bash
# Autonomous research loop from inquiry to paper
xavier research "Thermal stability and relaxation dynamics in core-shell nanoparticles"

# Ingest an existing codebase or dataset into the literature review
xavier research "Optimize learning rate decay" --codebase ./my_project

# Set custom auto-debugging retry limits
xavier research "Stochastic multi-strain SIR epidemic dynamics" --retries 5
```

---

### Inspect and Open Compiled Papers

```bash
# List all generated formats (PDF, LaTeX, HTML, Markdown)
xavier paper experiments/nanotechnology_20260904_0810

# Open compiled paper in default viewer/browser
xavier paper experiments/nanotechnology_20260904_0810 --open
```

---

### View Experiment History & Telemetry

```bash
# Inspect chronological experiment audit trail
xavier history --limit 10

# View active models, sandboxes, and provider keys
xavier config
```

---

## Output Artifacts

For every experiment, XavierLabs creates a dedicated, reproducible directory:

```text
experiments/nanotechnology_20260904_0810/
├── hypothesis.json          # Formulated hypothesis schema & parameters
├── review.json              # Peer-review assessment & critique score
├── experiment.py            # Self-contained computational simulation script
├── metrics.json             # Hard quantitative numerical results
├── plot.py                  # Matplotlib / Seaborn visualization code
├── plot.png                 # 300-DPI publication figure
├── paper.tex                # Formal arXiv LaTeX manuscript
├── paper.pdf                # Compiled academic publication PDF
├── paper.html               # Responsive interactive academic paper
└── report.md                # Comprehensive Markdown summary report
```

---

## Performance & Telemetry

| Metric | Groq (`compound-mini`) | DeepSeek (`deepseek-chat`) | Ollama (`deepseek-r1:8b`) |
| :--- | :--- | :--- | :--- |
| **Literature Retrieval** | 0.8s | 1.9s | 4.2s |
| **Hypothesis Generation** | 1.2s | 3.4s | 8.5s |
| **Code Synthesis** | 1.4s | 3.8s | 11.2s |
| **Simulation Execution** | 0.9s | 0.9s | 0.9s (Local CPU) |
| **Paper Compilation** | 1.8s | 4.2s | 9.8s |
| **End-to-End Run Duration**| **~6.1s** | **~14.2s** | **~34.6s** |

---

## Citation

If you use XavierLabs AI in your research or academic coursework, please cite:

```bibtex
@software{xavierlabs2026,
  author = {Moral, Adrian Xavier and XavierLabs Contributors},
  title = {XavierLabs AI: Autonomous Computational Scientific Research Swarm},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/venstqs/XavierLabs-AI}
}
```

---

## License

Distributed under the **MIT License**. See `LICENSE` for details.
Created by [Adrian Xavier Moral (@venstqs)](https://github.com/venstqs).
