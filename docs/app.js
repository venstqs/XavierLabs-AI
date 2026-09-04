// XavierLabs AI — Streamlined Interactive Terminal Logic

const installCommands = {
  pip: 'pip install git+https://github.com/venstqs/XavierLabs-AI.git',
  uv: 'uv pip install git+https://github.com/venstqs/XavierLabs-AI.git',
  git: 'git clone https://github.com/venstqs/XavierLabs-AI.git && cd XavierLabs-AI && pip install -e .'
};

const TERMINAL_SCRIPTS = {
  research: [
    { text: 'xavier research "Thermal relaxation kinetics in functionalized nanoparticles"', delay: 20, isInput: true },
    { text: '\n[dim]Initializing autonomous computational research swarm...[/dim]\n[dim]Sandbox: Local Isolated Subprocess | Provider: Groq (groq/compound-mini)[/dim]\n\n', delay: 80 },
    { text: '[cyan bold]● THE IDEATOR[/cyan bold] Synthesizing literature & hypothesis formulation...\n', delay: 150 },
    { text: '  • [bold]Thermodynamic Stability of PEGylated Lipid Envelopes[/bold] (2024) — [dim]arxiv.org/abs/2401.09112[/dim]\n  • [bold]Langevin Dynamics in Nanoparticle Drug Carriers[/bold] (2023) — [dim]arxiv.org/abs/2308.04155[/dim]\n', delay: 200 },
    { text: '  Formulated Hypothesis: [bold]Oscillatory thermal stress induces critical damping threshold &omega;c &asymp; 2.41e6 rad/s.[/bold]\n\n', delay: 180 },
    { text: '[yellow bold]● THE REVIEWER[/yellow bold] Adversarial audit & theoretical rigor check...\n  Audit Assessment: [green bold]APPROVED (Score: 9.2/10)[/green bold]\n\n', delay: 250 },
    { text: '[green bold]● THE CODER[/green bold] Synthesizing computational simulation (experiment.py)...\n', delay: 200 },
    { text: '[dim]Executing in sandbox containment (Timeout: 120s)...[/dim]\n', delay: 150 },
    { text: '  Process complete (Return Code 0 | Duration: 0.88s)\n  Extracted Metrics:\n    • tau_relaxation_us: 8.32\n    • critical_lysis_prob: 0.089\n    • free_energy_dissipation_kj: -28.4\n    • stability_gain: 2.21x\n\n', delay: 200 },
    { text: '[magenta bold]● THE SYNTHESIZER[/magenta bold] Compiling publication artifacts...\n  ✔ Rendered publication figure: plot.png (300 DPI)\n  ✔ Synthesized formal LaTeX manuscript: paper.tex\n  ✔ Compiled camera-ready PDF: paper.pdf\n  ✔ Compiled Markdown report: report.md\n\n', delay: 250 },
    { text: '[green bold]✔ Research run completed successfully. Artifacts saved to experiments/nanoparticles_20260904/[/green bold]\n', delay: 100 }
  ],
  chat: [
    { text: 'xavier', delay: 20, isInput: true },
    { text: '\n[bold green]XavierLabs Interactive Research Console[/bold green]\n[dim]Connected to Groq compound-mini | Type /help for available commands[/dim]\n\n', delay: 80 },
    { text: '[bold green]xavier [ready] › [/bold green]How can we study non-convex loss landscapes in optimizers?\n', delay: 25, isInput: true },
    { text: '[cyan bold]● THE IDEATOR[/cyan bold] We can formulate an in-silico comparison between AdamW and Lion:\n  1. Synthesize high-dimensional non-convex Rastrigin or Ackley loss surfaces.\n  2. Compute gradient variance and convergence steps across 10,000 iterations.\n\n[bold green]Launch autonomous research run on this topic? [Y/n]: [/bold green]y\n', delay: 200 },
    { text: '[green bold]▶ Swarm launched: Literature -> Code -> Auto-Debug -> LaTeX Paper[/green bold]\n', delay: 100 }
  ],
  paper: [
    { text: 'xavier paper experiments/nanoparticles_20260904 --open', delay: 20, isInput: true },
    { text: '\n[bold cyan]Compiled Academic Artifacts (nanoparticles_20260904)[/bold cyan]\n', delay: 100 },
    { text: '┌──────────────────┬────────────┬────────────────────────────────────────────────────────┐\n│ Artifact         │ Status     │ Path                                                   │\n├──────────────────┼────────────┼────────────────────────────────────────────────────────┤\n│ Publication PDF  │ [green bold]Ready[/green bold]      │ experiments/nanoparticles_20260904/paper.pdf           │\n│ LaTeX Source     │ [green bold]Ready[/green bold]      │ experiments/nanoparticles_20260904/paper.tex           │\n│ High-DPI Plot    │ [green bold]Ready[/green bold]      │ experiments/nanoparticles_20260904/plot.png            │\n│ Markdown Report  │ [green bold]Ready[/green bold]      │ experiments/nanoparticles_20260904/report.md           │\n└──────────────────┴────────────┴────────────────────────────────────────────────────────┘\n', delay: 150 },
    { text: '[green bold]✔ Opening paper.pdf in default system viewer...[/green bold]\n', delay: 100 }
  ],
  history: [
    { text: 'xavier history', delay: 20, isInput: true },
    { text: '\n[bold cyan]Experiment Telemetry & History[/bold cyan]\n', delay: 100 },
    { text: '┌────┬──────────────────┬────────────────────────────────────────────────┬───────────┬───────────┐\n│ ID │ Date             │ Topic                                          │ Status    │ Artifacts │\n├────┼──────────────────┼────────────────────────────────────────────────┼───────────┼───────────┤\n│ 4  │ 2026-09-04 08:10 │ Thermal relaxation kinetics in nanoparticles   │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 3  │ 2026-09-04 00:15 │ Sparse attention scaling on sequences          │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 2  │ 2026-09-03 23:42 │ Convergence of AdamW vs Lion optimizer         │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 1  │ 2026-09-03 21:10 │ Monte Carlo estimation benchmarks              │ [green bold]COMPLETED[/green bold] │ 5 files   │\n└────┴──────────────────┴────────────────────────────────────────────────┴───────────┴───────────┘\n', delay: 150 }
  ]
};

let currentToken = 0;
let currentInterval = null;
let currentTimeout = null;

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
  }, 2200);
}

function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text);
  }
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  document.execCommand('copy');
  document.body.removeChild(ta);
  return Promise.resolve();
}

function stopTerminal() {
  if (currentInterval) {
    clearInterval(currentInterval);
    currentInterval = null;
  }
  if (currentTimeout) {
    clearTimeout(currentTimeout);
    currentTimeout = null;
  }
}

function runTerminal(cmdKey) {
  const screen = document.getElementById('terminalBody');
  if (!screen) return;

  stopTerminal();
  const token = ++currentToken;
  screen.innerHTML = '';

  const script = TERMINAL_SCRIPTS[cmdKey] || TERMINAL_SCRIPTS['research'];
  let step = 0;

  function next() {
    if (token !== currentToken) return;
    if (step >= script.length) {
      screen.innerHTML += `\n<div class="term-prompt-line"><span class="term-prompt">xavier@lab:~$</span> <span class="cursor-blink"></span></div>`;
      screen.scrollTop = screen.scrollHeight;
      return;
    }

    const item = script[step];
    step++;

    if (item.isInput) {
      const p = document.createElement('div');
      p.className = 'term-prompt-line';
      p.innerHTML = `<span class="term-prompt">xavier@lab:~$</span> <span class="typed-text"></span><span class="cursor-blink"></span>`;
      screen.appendChild(p);

      const span = p.querySelector('.typed-text');
      const cursor = p.querySelector('.cursor-blink');
      let idx = 0;

      currentInterval = setInterval(() => {
        if (token !== currentToken) {
          clearInterval(currentInterval);
          return;
        }
        if (idx < item.text.length) {
          span.textContent += item.text[idx];
          idx++;
          screen.scrollTop = screen.scrollHeight;
        } else {
          clearInterval(currentInterval);
          currentInterval = null;
          if (cursor) cursor.remove();
          currentTimeout = setTimeout(next, 120);
        }
      }, 14);
    } else {
      screen.innerHTML += formatTerminalTags(item.text);
      screen.scrollTop = screen.scrollHeight;
      currentTimeout = setTimeout(next, item.delay || 100);
    }
  }

  next();
}

function init() {
  // Install tab switching
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

  // Install copy button
  const btnCopyInstall = document.getElementById('btnCopyInstall');
  if (btnCopyInstall) {
    btnCopyInstall.addEventListener('click', () => {
      const activeTab = document.querySelector('.tab-btn.active');
      const type = activeTab ? activeTab.dataset.tab : 'pip';
      const text = installCommands[type];
      copyToClipboard(text).then(() => showToast('Install command copied'));
    });
  }

  // General copy buttons
  document.querySelectorAll('[data-copy-code]').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = btn.getAttribute('data-copy-code');
      copyToClipboard(code).then(() => showToast('Copied to clipboard'));
    });
  });

  // Terminal tab switching
  document.querySelectorAll('.term-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.term-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      runTerminal(tab.dataset.cmd);
    });
  });

  // Start default terminal run
  runTerminal('research');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
