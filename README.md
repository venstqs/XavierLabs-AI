# XavierLabs AI
### Autonomous, Terminal-Native Computational Scientific Research Swarm

XavierLabs AI is an autonomous, terminal-native research engine designed to execute the computational scientific method end-to-end. Operating as a decentralized swarm of specialized AI agents deployed directly from the CLI, the system automates:
- **Literature Review & Discovery** (ArXiv, Semantic Scholar, Web)
- **Novel Mathematical Hypothesis Generation** (Strict JSON schemas)
- **Peer-Review Simulation** (Novelty critique & pre-flight code audits)
- **Code Execution & Containment** (Isolated Docker & Subprocess Sandboxes)
- **Automated Traceback Debugging** (Self-healing feedback loop)
- **Academic Manuscript & Figure Synthesis** (LaTeX, PDF, and Matplotlib/Seaborn)

---

## System Architecture: The Agentic Loop

```
                         ┌──────────────────────────────┐
                         │   User / High-Level Query    │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                      ┌────────────────────────────────────┐
                      │     The Ideator (Discovery)        │
                      │  - Queries ArXiv / Semantic Scholar│
                      │  - Ingests codebases/literature    │
                      │  - Emits JSON hypothesis config    │
                      └─────────────────┬──────────────────┘
                                        │
                                        ▼
                      ┌────────────────────────────────────┐
                      │    The Reviewer (Critique & Logic) │
                      │  - Peer-reviews hypothesis novelty │
                      │  - Audits Coder scripts pre-run    │
                      └─────────────────┬──────────────────┘
                                        │
                          [Approved]    ▼
                      ┌────────────────────────────────────┐
                      │      The Coder (Execution)         │
                      │  - Generates experiment.py         │
                      │  - Metrics logging & data pipeline │
                      └─────────────────┬──────────────────┘
                                        │
                                        ▼
                      ┌────────────────────────────────────┐
 ◄─────────────────── │   Sandbox Runtime (Docker / Local) │
 │ Auto-Debugging     │  - Executes experiment.py          │
 │ Feedback Loop      │  - Captures stdout/stderr telemetry│
 └─────────────────── └─────────────────┬──────────────────┘
                          [Success]     │
                                        ▼
                      ┌────────────────────────────────────┐
                      │    The Synthesizer (Artifacts)     │
                      │  - Generates plot.py (visuals)     │
                      │  - Compiles LaTeX / PDF report     │
                      └────────────────────────────────────┘
```

---

## Key Features

### 1. Universal Model & Provider Routing (LiteLLM)
Use **ANY** AI provider or local runner:
- **OpenRouter** (`OPENROUTER_API_KEY`): Access 100+ models (DeepSeek R1, Claude 3.5 Sonnet, Llama 3.3, Qwen 2.5) with one key.
- **DeepSeek Direct** (`DEEPSEEK_API_KEY`): Direct API for `deepseek-chat` and `deepseek-reasoner`.
- **Local Ollama** (Zero API keys needed!): Run completely offline with `ollama/deepseek-r1` or `ollama/qwen2.5-coder`.
- **OpenCode & Local Endpoints** (`OPENAI_API_BASE`): Connect LM Studio, vLLM, LocalAI, or custom OpenAI-compatible servers.
- **Frontier Providers**: Native support for **Google Gemini**, **Groq**, **OpenAI**, and **Anthropic Claude**.

### 2. Dual Sandbox Engine with Auto-Debugging
- **Docker SDK Sandbox**: Containment inside ephemeral containers mounting the experiment workspace.
- **Local Subprocess Sandbox**: Secure local fallback with process isolation, strict timeouts, and clean working directory isolation.
- **Traceback Auto-Debugger**: If an experiment crashes, the system captures stderr tracebacks, passes them back to the Coder agent, and autonomously repairs and re-runs the code until completion.

### 3. Feynman-Style Reactive Terminal Telemetry
Rendered with **Python Typer & Rich**:
- Cyberpunk scientific ASCII banner.
- Real-time agent status spinners.
- Formatted hypothesis and peer-review grading tables.
- Live telemetry execution panels with metrics and duration.
- Formatted markdown report streaming.

### 4. Stateful Experiment History
All experiments, hypotheses, code iterations, execution logs, and compiled artifacts are tracked in a persistent local **SQLite** database (`xavierlabs.db`).

---

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd "Research Agent"

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate  # Linux/macOS

# Install dependencies in editable mode
pip install -e .
```

---

## Configuration (`.env`)

Copy the `.env.example` file to `.env` and set whichever key you prefer:

```bash
cp .env.example .env
```

Example options (choose any one):
```env
# Option A: OpenRouter (DeepSeek, Claude, Llama 3)
OPENROUTER_API_KEY=sk-or-v1-...

# Option B: DeepSeek Direct API
DEEPSEEK_API_KEY=sk-...

# Option C: 100% Free Local Offline (Ollama - NO KEYS NEEDED)
# OLLAMA_API_BASE=http://localhost:11434
# DEFAULT_MODEL=ollama/deepseek-r1

# Option D: Google Gemini / OpenAI / Anthropic / Groq
GEMINI_API_KEY=AIzaSy...
# or: OPENAI_API_KEY=sk-...
# or: GROQ_API_KEY=gsk_...
```

---

## CLI Usage & Interactive Modes

### 1. Interactive Chatbot Mode (Antigravity CLI-Style)
Launch an interactive scientific research companion in your terminal:
```bash
xavier
# or: xavier chat
```
- **Conversational Ideation**: Chat conversationally about research ideas, optimizer algorithms, or physics simulations before running them.
- **Visual State Indicator**: The prompt tells you your current mode and active research (`xavier [ready] › ` vs `xavier [researching: nanotechnology...] › `).
- **Slash Commands**:
  - `/research <topic>` - Launch autonomous swarm execution
  - `/paper` - Inspect recent papers or open PDFs interactively
  - `/history` - View past experiment records
  - `/model` - Switch models on the fly (OpenRouter, DeepSeek, Ollama, Gemini)
  - `/config` - View active keys and telemetry
  - `/clear` - Clear screen
  - `/help` - Show all commands
  - `/exit` - Quit session

---

### 2. Direct Autonomous Research (One-Liner)
```bash
# Trigger the complete agentic loop directly
xavier research "Investigate sparse attention vs full attention scaling on synthetic sequences"

# Ingest an existing codebase or dataset
xavier research "Optimize learning rate schedules" --codebase ./my_data

# Specify max auto-debugging attempts
xavier research "Analyze AdamW vs Lion optimizer on non-convex loss landscapes" --retries 4
```

### 2. Run Isolated Script in Sandbox
```bash
xavier run experiments/my_exp/experiment.py --timeout 60
```

### 3. Inspect or Open Complete Research Paper
```bash
# View all paper formats (PDF, HTML, LaTeX, Markdown) for an experiment
xavier paper experiments/my_exp

# Automatically open the compiled PDF or publication paper in your browser
xavier paper experiments/my_exp --open
```

### 4. Inspect Experiment History
```bash
xavier history --limit 10
```

### 5. Check System Configuration & Telemetry
```bash
xavier config
```
