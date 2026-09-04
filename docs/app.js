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

const DEMO_SCRIPTS = {
  chat: [
    { text: 'xavier', delay: 30, isInput: true },
    { text: '\n[bold green]XavierLabs AI Interactive Console[/bold green]\n[dim]Active Model: openrouter/deepseek/deepseek-r1 | Sandbox: Local Subprocess[/dim]\n\n', delay: 100 },
    { text: '[bold #9ec97b]xavier[/bold #9ec97b] [dim]›[/dim] /help\n', delay: 35, isInput: true },
    { text: '┌────────────────────────┬─────────────────────────────────────────────────┐\n│ Command                │ Description                                     │\n├────────────────────────┼─────────────────────────────────────────────────┤\n│ /research <topic>      │ Launch autonomous research loop                 │\n│ /paper [folder]        │ Inspect or open compiled research paper         │\n│ /history               │ Browse and inspect past experiment records      │\n│ /model [name]          │ Switch model (OpenRouter, DeepSeek, Ollama)     │\n│ /config                │ View compute telemetry & detected API keys      │\n│ /exit                  │ Exit interactive session                        │\n└────────────────────────┴─────────────────────────────────────────────────┘\n\n', delay: 150 },
    { text: '[bold #9ec97b]xavier[/bold #9ec97b] [dim]›[/dim] I want to study sparse attention on non-convex loss\n', delay: 35, isInput: true },
    { text: '[cyan bold]● THE IDEATOR[/cyan bold] Analyzing hypothesis novelty and testable metrics...\n  • Proposed hypothesis: Sparse top-k attention stabilizes gradient variance by ~34%.\n\n[bold green]Would you like XavierLabs to launch an autonomous research run on this topic now? [Y/n]:[/bold green] y\n', delay: 200 },
    { text: '\n[bold #9ec97b]▶ Launching Autonomous Research Swarm...[/bold #9ec97b]\n  [green]✔ Swarm active: literature -> code -> auto-debug -> LaTeX paper[/green]\n', delay: 100 }
  ],
  research: [
    { text: 'xavier research "Analyze convergence of AdamW vs Lion on non-convex loss"', delay: 30, isInput: true },
    { text: '\n[bold green]Execution Sandbox:[/bold green] Local Isolated Subprocess Sandbox\n', delay: 120 },
    { text: '[cyan bold]● THE IDEATOR (IDEATOR)[/cyan bold] Querying ArXiv & Semantic Scholar...\n', delay: 180 },
    { text: '  • [bold]Symbolic Discovery of Optimization Algorithms[/bold] (2023) - [dim]arxiv.org/abs/2302.06675[/dim]\n  • [bold]Decoupled Weight Decay Regularization[/bold] (2019) - [dim]arxiv.org/abs/1711.05101[/dim]\n', delay: 250 },
    { text: '[yellow bold]● THE REVIEWER (REVIEWER)[/yellow bold] Auditing hypothesis novelty & theoretical rigor...\n  Peer Review Assessment: [green bold]APPROVED (Score: 8.8/10)[/green bold]\n', delay: 300 },
    { text: '[green bold]● THE CODER (CODER)[/green bold] Generating experiment.py with reproducibility seeds...\n', delay: 220 },
    { text: '[cyan bold]● EXECUTION SANDBOX[/cyan bold] Running experiment.py in isolated sandbox...\n', delay: 250 },
    { text: '  Duration: 0.84s | Return Code: 0\n  Parsed Metrics:\n    • adamw_final_loss: 0.00342\n    • lion_final_loss: 0.00189\n    • lion_speedup: 1.48x\n', delay: 180 },
    { text: '[magenta bold]● THE SYNTHESIZER (SYNTHESIZER)[/magenta bold] Compiling scientific artifacts...\n  ✔ Generated plot.py & rendered plot.png\n  ✔ Drafted academic LaTeX manuscript (paper.tex)\n  ✔ Compiled publication PDF: paper.pdf\n  ✔ Compiled Markdown report: report.md\n', delay: 300 },
    { text: '\n[green bold]✔ Research completed successfully. All artifacts saved to experiments/adamw_vs_lion_20260904/[/green bold]\n', delay: 100 }
  ],
  paper: [
    { text: 'xavier paper experiments/sparse_attention --open', delay: 30, isInput: true },
    { text: '\n[bold cyan]Research Paper Artifacts (sparse_attention)[/bold cyan]\n', delay: 120 },
    { text: '┌──────────────────┬────────────┬──────────────────────────────────────────┐\n│ Format           │ Status     │ File Path                                │\n├──────────────────┼────────────┼──────────────────────────────────────────┤\n│ Publication PDF  │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/paper.pdf   │\n│ Academic HTML    │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/paper.html  │\n│ LaTeX Source     │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/paper.tex   │\n│ Markdown Report  │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/report.md   │\n└──────────────────┴────────────┴──────────────────────────────────────────┘\n', delay: 180 },
    { text: '[green bold]✔ Opening paper.pdf in default viewer...[/green bold]\n', delay: 120 }
  ],
  history: [
    { text: 'xavier history', delay: 30, isInput: true },
    { text: '\n[bold cyan]XavierLabs AI Research History[/bold cyan]\n', delay: 120 },
    { text: '┌────┬──────────────────┬────────────────────────────────────────┬───────────┬───────────┐\n│ ID │ Date             │ Topic                                  │ Status    │ Artifacts │\n├────┼──────────────────┼────────────────────────────────────────┼───────────┼───────────┤\n│ 3  │ 2026-09-04 00:15 │ Sparse attention scaling on sequences  │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 2  │ 2026-09-03 23:42 │ Convergence of AdamW vs Lion optimizer │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 1  │ 2026-09-03 21:10 │ Monte Carlo estimation benchmarks      │ [green bold]COMPLETED[/green bold] │ 5 files   │\n└────┴──────────────────┴────────────────────────────────────────┴───────────┴───────────┘\n', delay: 180 }
  ],
  config: [
    { text: 'xavier config', delay: 30, isInput: true },
    { text: '\n[bold cyan]XavierLabs AI Configuration & Compute Telemetry[/bold cyan]\n', delay: 120 },
    { text: '┌───────────────────────────┬─────────────────────────────────────────────────┐\n│ Component                 │ Configured Value                                │\n├───────────────────────────┼─────────────────────────────────────────────────┤\n│ Execution Sandbox         │ Local Isolated Subprocess Sandbox (Fallback)    │\n│ Active/Auto Model         │ [cyan bold]openrouter/deepseek/deepseek-r1[/cyan bold]       │\n│ Ideator Model             │ auto                                            │\n│ Reviewer Model            │ auto (or local ollama/deepseek-r1)              │\n│ Coder Model               │ auto                                            │\n│ Synthesizer Model         │ auto                                            │\n│ OPENROUTER_API_KEY        │ [green bold]Detected[/green bold]                                        │\n│ DEEPSEEK_API_KEY          │ [green bold]Detected[/green bold]                                        │\n│ OLLAMA_API_BASE           │ http://localhost:11434                          │\n│ Database Engine           │ SQLite (xavierlabs.db)                          │\n└───────────────────────────┴─────────────────────────────────────────────────┘\n', delay: 180 }
  ]
};

// 2. State Variables
var currentDemoToken = 0;
var currentInterval = null;
var currentTimeout = null;

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

// 4. Feature Modules
function initInstallTabs() {
  const tabs = document.querySelectorAll('.tab-btn, .install-tab');
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
        const activeTab = document.querySelector('.tab-btn.active, .install-tab.active');
        const type = activeTab ? activeTab.dataset.tab : 'pip';
        textToCopy = installCommands[type] || '';
      } else {
        const targetEl = document.getElementById(targetId);
        if (targetEl) textToCopy = targetEl.innerText.replace(/^\$\s*/, '').trim();
      }

      if (textToCopy) {
        copyToClipboard(textToCopy).then(() => {
          showToast(`Copied: "${textToCopy.substring(0, 34)}..."`);
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

function runTerminalDemo(cmdKey) {
  const termBody = document.getElementById('terminalBody');
  if (!termBody) return;

  stopTerminalDemo();
  const token = ++currentDemoToken;

  termBody.innerHTML = `<div class="term-logo term-pixel-logo">${escapeHtml(PIXEL_BANNER.trim())}</div>\n`;

  const script = DEMO_SCRIPTS[cmdKey] || DEMO_SCRIPTS['research'];
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
          currentTimeout = setTimeout(nextStep, 200);
        }
      }, 20);
    } else {
      const formatted = formatTerminalTags(item.text);
      termBody.innerHTML += formatted;
      termBody.scrollTop = termBody.scrollHeight;
      currentTimeout = setTimeout(nextStep, item.delay || 120);
    }
  }

  nextStep();
}

function initTerminal() {
  const tabs = document.querySelectorAll('.term-tab, .pill-cmd');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const cmd = tab.dataset.cmd;
      runTerminalDemo(cmd);
    });
  });

  // Load initial interactive chat demo
  runTerminalDemo('chat');
}

// 5. App Initialization
function initApp() {
  initInstallTabs();
  initCopyButtons();
  initTerminal();
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }
}
