// XavierLabs AI - Interactive Landing Page Logic

// 1. Static Configuration & Scripts
const installCommands = {
  pip: 'pip install git+https://github.com/venstqs/XavierLabs-AI.git',
  uv: 'uv pip install git+https://github.com/venstqs/XavierLabs-AI.git',
  git: 'git clone https://github.com/venstqs/XavierLabs-AI.git && cd XavierLabs-AI && pip install -e .'
};

const PIXEL_BANNER = `
                        █                   ██           █            
                                             █           █            
 █   █   ████  ██ ██   ██     ███   █ ██     █     ████  ████    ████ 
  █ █   █   █   █ █     █    █   █  ██       █    █   █  █   █  █     
   █    █   █   █ █     █    █████  █        █    █   █  █   █   ███  
  █ █   █  ██    █      █    █      █        █    █  ██  █   █      █ 
 █   █   ██ █    █     ███    ███   █       ███    ██ █  ████   ████  

       x a v i e r l a b s • terminal-native computational research swarm
`;

const TOPIC_PRESETS = {
  nanotechnology: {
    title: 'Nanotechnology drug delivery stability',
    query: 'xavier research "Thermodynamic relaxation & membrane lysis kinetics in core-shell lipid nanoparticles"',
    papers: [
      '• [bold]Thermodynamic Stability of PEGylated Lipid Envelopes[/bold] (2024) - [dim]arxiv.org/abs/2401.09112[/dim]',
      '• [bold]Brownian Dynamics in Nanoparticle Drug Carriers[/bold] (2023) - [dim]arxiv.org/abs/2308.04155[/dim]'
    ],
    score: '9.2/10 (EXEMPLARY)',
    metrics: [
      '• tau_relaxation_us: 8.32',
      '• critical_lysis_prob: 0.089',
      '• free_energy_gain_kj: -28.4',
      '• membrane_stability_ratio: 2.21x'
    ],
    folder: 'experiments/nanotechnology_20260904_0810/'
  },
  adamw_vs_lion: {
    title: 'AdamW vs Lion Optimizer',
    query: 'xavier research "Analyze convergence of AdamW vs Lion on non-convex loss landscapes"',
    papers: [
      '• [bold]Symbolic Discovery of Optimization Algorithms[/bold] (2023) - [dim]arxiv.org/abs/2302.06675[/dim]',
      '• [bold]Decoupled Weight Decay Regularization[/bold] (2019) - [dim]arxiv.org/abs/1711.05101[/dim]'
    ],
    score: '8.8/10 (APPROVED)',
    metrics: [
      '• adamw_final_loss: 0.00342',
      '• lion_final_loss: 0.00189',
      '• speedup_relative: 1.48x',
      '• gradient_variance_reduction: 34.1%'
    ],
    folder: 'experiments/adamw_vs_lion_20260904_1120/'
  },
  quantum_dots: {
    title: 'Quantum Dots Thermal Stress Dynamics',
    query: 'xavier research "Non-equilibrium phonon scattering and thermal stress relaxation in core-shell quantum dots"',
    papers: [
      '• [bold]Phonon Bottleneck in Colloidal Nanocrystal Quantum Dots[/bold] (2022) - [dim]arxiv.org/abs/2205.11422[/dim]',
      '• [bold]Exciton Dynamics under High Thermal Flux[/bold] (2023) - [dim]arxiv.org/abs/2304.09811[/dim]'
    ],
    score: '9.0/10 (APPROVED)',
    metrics: [
      '• carrier_relaxation_time_ps: 1.42',
      '• quantum_yield_retention: 94.6%',
      '• thermal_conductivity_w_mk: 4.82',
      '• phonon_mean_free_path_nm: 18.5'
    ],
    folder: 'experiments/quantum_dots_20260904_1402/'
  },
  epidemic_sir: {
    title: 'Multi-Strain SIR Epidemic Dynamics',
    query: 'xavier research "Stochastic multi-strain SIR dynamics with heterogeneous transmission and spatial mobility"',
    papers: [
      '• [bold]Stochastic Network Epidemic Models[/bold] (2021) - [dim]arxiv.org/abs/2103.04512[/dim]',
      '• [bold]Bifurcation Analysis in Competing Pathogen Strains[/bold] (2023) - [dim]arxiv.org/abs/2301.07720[/dim]'
    ],
    score: '8.9/10 (APPROVED)',
    metrics: [
      '• r0_effective_strain_a: 1.34',
      '• r0_effective_strain_b: 2.18',
      '• herd_immunity_threshold: 54.2%',
      '• peak_hospitalization_rate: 0.041'
    ],
    folder: 'experiments/sir_epidemic_20260904_1630/'
  }
};

const DEMO_SCRIPTS = {
  chat: [
    { text: 'xavier', delay: 30, isInput: true },
    { text: '\n[bold green]XavierLabs AI Interactive Console[/bold green]\n[dim]Active Model: groq/groq/compound-mini | Sandbox: Local Subprocess Sandbox[/dim]\n\n', delay: 100 },
    { text: '[bold #9ec97b]xavier[/bold #9ec97b] [dim]›[/dim] /help\n', delay: 35, isInput: true },
    { text: '┌────────────────────────┬─────────────────────────────────────────────────┐\n│ Command                │ Description                                     │\n├────────────────────────┼─────────────────────────────────────────────────┤\n│ /research <topic>      │ Launch autonomous research loop                 │\n│ /paper [folder]        │ Inspect or open compiled research paper         │\n│ /history               │ Browse and inspect past experiment records      │\n│ /model [name]          │ Switch model (Groq, OpenRouter, DeepSeek, Ollama)│\n│ /config                │ View compute telemetry & detected API keys      │\n│ /exit                  │ Exit interactive session                        │\n└────────────────────────┴─────────────────────────────────────────────────┘\n\n', delay: 150 },
    { text: '[bold #9ec97b]xavier[/bold #9ec97b] [dim]›[/dim] I want to study lipid nanoparticle drug delivery stability\n', delay: 35, isInput: true },
    { text: '[cyan bold]● THE IDEATOR[/cyan bold] Synthesizing hypothesis & literature retrieval...\n  • Proposed hypothesis: PEGylated lipid shells reduce lysis probability by ~74%.\n\n[bold green]Would you like XavierLabs to launch an autonomous research run on this topic now? [Y/n]:[/bold green] y\n', delay: 200 },
    { text: '\n[bold #9ec97b]▶ Launching Autonomous Research Swarm...[/bold #9ec97b]\n  [green]✔ Swarm active: literature -> code -> auto-debug -> LaTeX paper[/green]\n', delay: 100 }
  ],
  research: [
    { text: 'xavier research "Thermodynamic relaxation in functionalized lipid nanoparticles"', delay: 30, isInput: true },
    { text: '\n[bold green]Execution Sandbox:[/bold green] Local Isolated Subprocess Sandbox\n', delay: 120 },
    { text: '[cyan bold]● THE IDEATOR (IDEATOR)[/cyan bold] Querying ArXiv & Semantic Scholar...\n', delay: 180 },
    { text: '  • [bold]Thermodynamic Stability of PEGylated Lipid Envelopes[/bold] (2024) - [dim]arxiv.org/abs/2401.09112[/dim]\n  • [bold]Brownian Dynamics in Nanoparticle Drug Carriers[/bold] (2023) - [dim]arxiv.org/abs/2308.04155[/dim]\n', delay: 250 },
    { text: '[yellow bold]● THE REVIEWER (REVIEWER)[/yellow bold] Auditing hypothesis novelty & theoretical rigor...\n  Peer Review Assessment: [green bold]APPROVED (Score: 9.2/10)[/green bold]\n', delay: 300 },
    { text: '[green bold]● THE CODER (CODER)[/green bold] Generating experiment.py with Langevin dynamics integration...\n', delay: 220 },
    { text: '[cyan bold]● EXECUTION SANDBOX[/cyan bold] Running experiment.py in isolated sandbox...\n', delay: 250 },
    { text: '  Duration: 0.92s | Return Code: 0\n  Parsed Metrics:\n    • tau_relaxation_us: 8.32\n    • critical_lysis_prob: 0.089\n    • free_energy_gain_kj: -28.4\n    • membrane_stability_gain: 2.21x\n', delay: 180 },
    { text: '[magenta bold]● THE SYNTHESIZER (SYNTHESIZER)[/magenta bold] Compiling scientific artifacts...\n  ✔ Generated plot.py & rendered plot.png (300 DPI)\n  ✔ Drafted academic LaTeX manuscript (paper.tex)\n  ✔ Compiled publication PDF: paper.pdf\n  ✔ Compiled Markdown report: report.md\n', delay: 300 },
    { text: '\n[green bold]✔ Research completed successfully. All artifacts saved to experiments/nanotechnology_20260904/[/green bold]\n', delay: 100 }
  ],
  paper: [
    { text: 'xavier paper experiments/nanotechnology_20260904 --open', delay: 30, isInput: true },
    { text: '\n[bold cyan]Research Paper Artifacts (nanotechnology_20260904)[/bold cyan]\n', delay: 120 },
    { text: '┌──────────────────┬────────────┬────────────────────────────────────────────────────┐\n│ Format           │ Status     │ File Path                                          │\n├──────────────────┼────────────┼────────────────────────────────────────────────────┤\n│ Publication PDF  │ [green bold]Ready[/green bold]      │ experiments/nanotechnology_20260904/paper.pdf      │\n│ Academic HTML    │ [green bold]Ready[/green bold]      │ experiments/nanotechnology_20260904/paper.html     │\n│ LaTeX Source     │ [green bold]Ready[/green bold]      │ experiments/nanotechnology_20260904/paper.tex      │\n│ Markdown Report  │ [green bold]Ready[/green bold]      │ experiments/nanotechnology_20260904/report.md      │\n└──────────────────┴────────────┴────────────────────────────────────────────────────┘\n', delay: 180 },
    { text: '[green bold]✔ Opening paper.pdf in default viewer...[/green bold]\n', delay: 120 }
  ],
  history: [
    { text: 'xavier history', delay: 30, isInput: true },
    { text: '\n[bold cyan]XavierLabs AI Research History[/bold cyan]\n', delay: 120 },
    { text: '┌────┬──────────────────┬────────────────────────────────────────────────┬───────────┬───────────┐\n│ ID │ Date             │ Topic                                          │ Status    │ Artifacts │\n├────┼──────────────────┼────────────────────────────────────────────────┼───────────┼───────────┤\n│ 4  │ 2026-09-04 08:10 │ Nanotechnology drug delivery stability        │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 3  │ 2026-09-04 00:15 │ Sparse attention scaling on sequences          │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 2  │ 2026-09-03 23:42 │ Convergence of AdamW vs Lion optimizer         │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 1  │ 2026-09-03 21:10 │ Monte Carlo estimation benchmarks              │ [green bold]COMPLETED[/green bold] │ 5 files   │\n└────┴──────────────────┴────────────────────────────────────────────────┴───────────┴───────────┘\n', delay: 180 }
  ],
  config: [
    { text: 'xavier config', delay: 30, isInput: true },
    { text: '\n[bold cyan]XavierLabs AI Configuration & Compute Telemetry[/bold cyan]\n', delay: 120 },
    { text: '┌───────────────────────────┬─────────────────────────────────────────────────┐\n│ Component                 │ Configured Value                                │\n├───────────────────────────┼─────────────────────────────────────────────────┤\n│ Execution Sandbox         │ Local Isolated Subprocess Sandbox (Fallback)    │\n│ Active/Auto Model         │ [cyan bold]groq/groq/compound-mini[/cyan bold]                   │\n│ Ideator Model             │ auto                                            │\n│ Reviewer Model            │ auto                                            │\n│ Coder Model               │ auto                                            │\n│ Synthesizer Model         │ auto                                            │\n│ GROQ_API_KEY              │ [green bold]Detected[/green bold]                                        │\n│ OPENROUTER_API_KEY        │ [green bold]Detected[/green bold]                                        │\n│ DEEPSEEK_API_KEY          │ [green bold]Detected[/green bold]                                        │\n│ Database Engine           │ SQLite (xavierlabs.db)                          │\n└───────────────────────────┴─────────────────────────────────────────────────┘\n', delay: 180 }
  ]
};

// 2. State Variables
let currentDemoToken = 0;
let currentInterval = null;
let currentTimeout = null;

// 3. Helper Functions
function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function formatTerminalTags(str) {
  return str
    .replace(/\[bold green\]([\s\S]*?)\[\/bold green\]/g, '<span class="term-green term-bold">$1</span>')
    .replace(/\[green bold\]([\s\S]*?)\[\/green bold\]/g, '<span class="term-green term-bold">$1</span>')
    .replace(/\[bold cyan\]([\s\S]*?)\[\/bold cyan\]/g, '<span class="term-cyan term-bold">$1</span>')
    .replace(/\[cyan bold\]([\s\S]*?)\[\/cyan bold\]/g, '<span class="term-cyan term-bold">$1</span>')
    .replace(/\[yellow bold\]([\s\S]*?)\[\/yellow bold\]/g, '<span class="term-yellow term-bold">$1</span>')
    .replace(/\[magenta bold\]([\s\S]*?)\[\/magenta bold\]/g, '<span class="term-magenta term-bold">$1</span>')
    .replace(/\[bold #9ec97b\]([\s\S]*?)\[\/bold #9ec97b\]/g, '<span class="term-green term-bold">$1</span>')
    .replace(/\[bold\]([\s\S]*?)\[\/bold\]/g, '<span class="term-bold">$1</span>')
    .replace(/\[dim\]([\s\S]*?)\[\/dim\]/g, '<span class="term-dim">$1</span>');
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.innerText = msg;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
  }
  fallbackCopy(text);
  return Promise.resolve();
}

function fallbackCopy(text) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.left = '-9999px';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    document.execCommand('copy');
  } catch (err) {
    console.error('Fallback copy failed', err);
  }
  document.body.removeChild(textArea);
}

// 4. Terminal Simulation Logic
function stopTerminalDemo() {
  if (currentInterval) {
    clearInterval(currentInterval);
    currentInterval = null;
  }
  if (currentTimeout) {
    clearTimeout(currentTimeout);
    currentTimeout = null;
  }
}

function runTerminalDemo(cmdKey, customScript = null) {
  const termBody = document.getElementById('terminalBody');
  if (!termBody) return;

  stopTerminalDemo();
  const token = ++currentDemoToken;

  termBody.innerHTML = `<div class="term-logo term-pixel-logo">${escapeHtml(PIXEL_BANNER.trim())}</div>\n`;

  const script = customScript || DEMO_SCRIPTS[cmdKey] || DEMO_SCRIPTS['research'];
  let stepIndex = 0;

  function nextStep() {
    if (token !== currentDemoToken) return;

    if (stepIndex >= script.length) {
      termBody.innerHTML += `\n<div class="term-prompt-line"><span class="term-prompt">xavier@lab:~$</span> <span class="cursor-blink"></span></div>`;
      termBody.scrollTop = termBody.scrollHeight;
      return;
    }

    const item = script[stepIndex];
    stepIndex++;

    if (item.isInput) {
      const promptDiv = document.createElement('div');
      promptDiv.className = 'term-prompt-line';
      promptDiv.innerHTML = `<span class="term-prompt">xavier@lab:~$</span> <span class="term-typed typed-input"></span><span class="cursor-blink"></span>`;
      termBody.appendChild(promptDiv);

      const targetSpan = promptDiv.querySelector('.typed-input');
      const cursor = promptDiv.querySelector('.cursor-blink');
      let charIdx = 0;

      currentInterval = setInterval(() => {
        if (token !== currentDemoToken) {
          clearInterval(currentInterval);
          return;
        }
        if (charIdx < item.text.length) {
          targetSpan.textContent += item.text[charIdx];
          charIdx++;
          termBody.scrollTop = termBody.scrollHeight;
        } else {
          clearInterval(currentInterval);
          currentInterval = null;
          if (cursor) cursor.remove();
          currentTimeout = setTimeout(nextStep, 150);
        }
      }, 16);
    } else {
      const formatted = formatTerminalTags(item.text);
      termBody.innerHTML += formatted;
      termBody.scrollTop = termBody.scrollHeight;
      currentTimeout = setTimeout(nextStep, item.delay || 120);
    }
  }

  nextStep();
}

function buildCustomTopicScript(topicName) {
  const preset = TOPIC_PRESETS[topicName] || {
    title: topicName,
    query: `xavier research "${topicName}"`,
    papers: [
      `• [bold]Mathematical Foundations of ${topicName}[/bold] (2024) - [dim]arxiv.org/abs/2403.01124[/dim]`,
      `• [bold]Stochastic Simulation Approaches in Computational Sciences[/bold] (2023) - [dim]arxiv.org/abs/2309.05581[/dim]`
    ],
    score: '8.9/10 (APPROVED)',
    metrics: [
      '• primary_convergence_rate: 0.00214',
      '• variance_reduction_ratio: 38.2%',
      '• execution_duration_sec: 1.14s'
    ],
    folder: `experiments/${topicName.toLowerCase().replace(/[^a-z0-9]+/g, '_')}_20260904/`
  };

  return [
    { text: preset.query, delay: 25, isInput: true },
    { text: '\n[bold green]Execution Sandbox:[/bold green] Local Isolated Subprocess Sandbox\n', delay: 100 },
    { text: '[cyan bold]● THE IDEATOR (IDEATOR)[/cyan bold] Literature retrieval & hypothesis formulation...\n', delay: 150 },
    { text: `  ${preset.papers.join('\n  ')}\n`, delay: 200 },
    { text: `[yellow bold]● THE REVIEWER (REVIEWER)[/yellow bold] Auditing theoretical rigor...\n  Assessment: [green bold]${preset.score}[/green bold]\n`, delay: 250 },
    { text: '[green bold]● THE CODER (CODER)[/green bold] Translating hypothesis into executable experiment.py...\n', delay: 200 },
    { text: '[cyan bold]● EXECUTION SANDBOX[/cyan bold] Running experiment.py in sandbox containment...\n', delay: 250 },
    { text: `  Execution Status: Return Code 0 | Duration: 0.88s\n  Parsed Numerical Metrics:\n    ${preset.metrics.join('\n    ')}\n`, delay: 180 },
    { text: `[magenta bold]● THE SYNTHESIZER (SYNTHESIZER)[/magenta bold] Compiling scientific artifacts...\n  ✔ Rendered publication plot: plot.png\n  ✔ Drafted academic LaTeX manuscript (paper.tex)\n  ✔ Compiled PDF report (paper.pdf)\n`, delay: 250 },
    { text: `\n[green bold]✔ Research completed successfully. All artifacts saved to ${preset.folder}[/green bold]\n`, delay: 100 }
  ];
}

// 5. Canvas Publication Chart Renderer
function drawPublicationChart() {
  const canvas = document.getElementById('paperChartCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;

  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = 220 * dpr;
  ctx.scale(dpr, dpr);

  const w = rect.width;
  const h = 220;
  const pad = { top: 25, right: 35, bottom: 40, left: 55 };

  // Background
  ctx.fillStyle = '#090c10';
  ctx.fillRect(0, 0, w, h);

  // Grid Lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
  ctx.lineWidth = 1;
  const yTicks = 4;
  for (let i = 0; i <= yTicks; i++) {
    const y = pad.top + (i / yTicks) * (h - pad.top - pad.bottom);
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(w - pad.right, y);
    ctx.stroke();

    // Y Axis Label
    ctx.fillStyle = '#484f58';
    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.textAlign = 'right';
    const val = (1.0 - (i / yTicks)).toFixed(1);
    ctx.fillText(val, pad.left - 8, y + 3);
  }

  // X Axis Label
  ctx.fillStyle = '#484f58';
  ctx.font = '10px "JetBrains Mono", monospace';
  ctx.textAlign = 'center';
  const xTicks = 5;
  for (let i = 0; i <= xTicks; i++) {
    const x = pad.left + (i / xTicks) * (w - pad.left - pad.right);
    ctx.fillText(`${i * 200} &mu;s`, x, h - pad.bottom + 18);
  }

  // Baseline Curve (Damped oscillation) - Gray/Red
  ctx.strokeStyle = '#f87171';
  ctx.lineWidth = 2;
  ctx.beginPath();
  const graphW = w - pad.left - pad.right;
  const graphH = h - pad.top - pad.bottom;

  for (let px = 0; px <= graphW; px += 2) {
    const t = px / graphW;
    const yVal = Math.exp(-2.2 * t) * Math.cos(t * Math.PI * 5) * 0.75;
    const normY = 0.5 - (yVal * 0.5);
    const canvasY = pad.top + normY * graphH;
    if (px === 0) ctx.moveTo(pad.left + px, canvasY);
    else ctx.lineTo(pad.left + px, canvasY);
  }
  ctx.stroke();

  // Engineered Curve - Sage Green (Fast exponential damping)
  ctx.strokeStyle = '#9ec97b';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  for (let px = 0; px <= graphW; px += 2) {
    const t = px / graphW;
    const yVal = Math.exp(-5.5 * t) * Math.cos(t * Math.PI * 3.5) * 0.8;
    const normY = 0.5 - (yVal * 0.5);
    const canvasY = pad.top + normY * graphH;
    if (px === 0) ctx.moveTo(pad.left + px, canvasY);
    else ctx.lineTo(pad.left + px, canvasY);
  }
  ctx.stroke();

  // Legend
  const legX = w - pad.right - 210;
  const legY = pad.top + 10;
  ctx.fillStyle = 'rgba(20, 25, 34, 0.85)';
  ctx.fillRect(legX - 8, legY - 8, 218, 46);
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
  ctx.strokeRect(legX - 8, legY - 8, 218, 46);

  // Line 1: Green
  ctx.strokeStyle = '#9ec97b';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(legX, legY + 5);
  ctx.lineTo(legX + 22, legY + 5);
  ctx.stroke();

  ctx.fillStyle = '#f0f6fc';
  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.textAlign = 'left';
  ctx.fillText('Engineered Core-Shell (Proposed)', legX + 28, legY + 8);

  // Line 2: Red
  ctx.strokeStyle = '#f87171';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(legX, legY + 22);
  ctx.lineTo(legX + 22, legY + 22);
  ctx.stroke();

  ctx.fillStyle = '#8b949e';
  ctx.fillText('Unfunctionalized Baseline', legX + 28, legY + 25);
}

// 6. UI Interaction Handlers
function initInstallTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const codeEl = document.getElementById('installCode');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const type = tab.dataset.tab;
      if (codeEl && installCommands[type]) {
        codeEl.innerHTML = `<span class="prompt">$</span>${escapeHtml(installCommands[type])}`;
      }
    });
  });
}

function initCopyButtons() {
  const copyButtons = document.querySelectorAll('[data-copy-target]');

  copyButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-copy-target');
      let textToCopy = '';

      if (targetId === 'installCode') {
        const activeTab = document.querySelector('.tab-btn.active');
        const type = activeTab ? activeTab.dataset.tab : 'pip';
        textToCopy = installCommands[type] || '';
      }

      if (textToCopy) {
        copyToClipboard(textToCopy).then(() => {
          showToast(`Copied: "${textToCopy.substring(0, 32)}..."`);
          const originalText = btn.innerHTML;
          btn.innerHTML = '✓ Copied';
          setTimeout(() => {
            btn.innerHTML = originalText;
          }, 2000);
        });
      }
    });
  });
}

function initPlayground() {
  const chips = document.querySelectorAll('.topic-chips .chip');
  const inputEl = document.getElementById('customTopicInput');
  const runBtn = document.getElementById('btnRunPlayground');
  const replayBtn = document.getElementById('btnReplayTerm');

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const topicKey = chip.dataset.topic;
      if (TOPIC_PRESETS[topicKey] && inputEl) {
        inputEl.value = TOPIC_PRESETS[topicKey].title;
      }
      const script = buildCustomTopicScript(topicKey);
      runTerminalDemo(null, script);
    });
  });

  if (runBtn && inputEl) {
    runBtn.addEventListener('click', () => {
      const val = inputEl.value.trim();
      if (!val) return;
      const script = buildCustomTopicScript(val);
      runTerminalDemo(null, script);
      showToast(`Launching swarm simulation for "${val.substring(0, 24)}..."`);
    });

    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        runBtn.click();
      }
    });
  }

  if (replayBtn) {
    replayBtn.addEventListener('click', () => {
      const activeTab = document.querySelector('.term-tab.active');
      const cmd = activeTab ? activeTab.dataset.cmd : 'research';
      runTerminalDemo(cmd);
    });
  }
}

function initTerminalTabs() {
  const tabs = document.querySelectorAll('.term-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const cmd = tab.dataset.cmd;
      runTerminalDemo(cmd);
    });
  });
}

function initPaperModal() {
  const modal = document.getElementById('paperModal');
  const openBtns = [document.getElementById('btnOpenPaperModal'), document.getElementById('btnOpenModalFull')];
  const closeBtn = document.getElementById('btnCloseModal');
  const copyLatexBtn = document.getElementById('btnCopyLatex');
  const copyBibtexBtn = document.getElementById('btnCopyBibtex');
  const downloadPdfBtn = document.getElementById('btnDownloadMockPdf');

  openBtns.forEach(btn => {
    if (btn) {
      btn.addEventListener('click', () => {
        if (modal) modal.classList.add('open');
      });
    }
  });

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('open');
    });
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('open');
    });
  }

  if (copyLatexBtn) {
    copyLatexBtn.addEventListener('click', () => {
      const sampleLatex = `\\documentclass[11pt,a4paper]{article}
\\usepackage{amsmath,amssymb,graphicx,booktabs,hyperref}
\\title{Thermal Stability and In-Silico Relaxation Dynamics in Core-Shell Functionalized Nanoparticles}
\\author{Adrian Xavier Moral \\and XavierLabs AI Computational Research Swarm}
\\begin{document}
\\maketitle
\\begin{abstract}
We report on the stochastic Langevin simulation of engineered lipid nanoparticles...
\\end{abstract}
\\section{Introduction}
...
\\end{document}`;
      copyToClipboard(sampleLatex).then(() => showToast('LaTeX source copied to clipboard!'));
    });
  }

  if (copyBibtexBtn) {
    copyBibtexBtn.addEventListener('click', () => {
      const bibtex = `@software{xavierlabs2026,
  author = {Moral, Adrian Xavier and XavierLabs Contributors},
  title = {XavierLabs AI: Autonomous Computational Scientific Research Swarm},
  year = {2026},
  url = {https://github.com/venstqs/XavierLabs-AI}
}`;
      copyToClipboard(bibtex).then(() => showToast('BibTeX citation copied to clipboard!'));
    });
  }

  if (downloadPdfBtn) {
    downloadPdfBtn.addEventListener('click', () => {
      showToast('Compiling manuscript PDF artifact...');
      setTimeout(() => {
        window.open('https://github.com/venstqs/XavierLabs-AI', '_blank');
      }, 1000);
    });
  }
}

// 7. App Initialization
function initApp() {
  initInstallTabs();
  initCopyButtons();
  initTerminalTabs();
  initPlayground();
  initPaperModal();

  // Draw chart on load & resize
  drawPublicationChart();
  window.addEventListener('resize', drawPublicationChart);

  // Initial terminal demo
  runTerminalDemo('research');
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }
}
