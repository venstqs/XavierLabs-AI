// XavierLabs AI - Interactive Landing Page Logic

document.addEventListener('DOMContentLoaded', () => {
  initInstallTabs();
  initCopyButtons();
  initTerminal();
});

// 1. Install Widget Tab Switcher
const installCommands = {
  pip: 'pip install git+https://github.com/venstqs/XavierLabs-AI.git',
  git: 'git clone https://github.com/venstqs/XavierLabs-AI.git && cd XavierLabs-AI && pip install -e .',
  uv: 'uv pip install git+https://github.com/venstqs/XavierLabs-AI.git'
};

function initInstallTabs() {
  const tabs = document.querySelectorAll('.install-tab');
  const codeEl = document.getElementById('installCode');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const type = tab.dataset.tab;
      if (codeEl && installCommands[type]) {
        codeEl.innerHTML = `<span class="prefix">$</span>${escapeHtml(installCommands[type])}`;
      }
    });
  });
}

// 2. Clipboard Copy with Toast
function initCopyButtons() {
  const copyButtons = document.querySelectorAll('[data-copy-target]');
  const toast = document.getElementById('toast');

  copyButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-copy-target');
      let textToCopy = '';

      if (targetId === 'installCode') {
        const activeTab = document.querySelector('.install-tab.active');
        const type = activeTab ? activeTab.dataset.tab : 'pip';
        textToCopy = installCommands[type] || '';
      } else {
        const targetEl = document.getElementById(targetId);
        if (targetEl) textToCopy = targetEl.innerText.replace(/^\$\s*/, '').trim();
      }

      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
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

function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.innerText = msg;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

// 3. Interactive Feynman Terminal Simulator
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
  research: [
    { text: 'xavier research "Analyze convergence of AdamW vs Lion on non-convex loss"', delay: 40, isInput: true },
    { text: '\n[bold green]Execution Sandbox:[/bold green] Local Isolated Subprocess Sandbox\n', delay: 150 },
    { text: '[cyan bold]● THE IDEATOR (IDEATOR)[/cyan bold] Querying ArXiv & Semantic Scholar...\n', delay: 200 },
    { text: '  • [bold]Symbolic Discovery of Optimization Algorithms[/bold] (2023) - [dim]arxiv.org/abs/2302.06675[/dim]\n  • [bold]Decoupled Weight Decay Regularization[/bold] (2019) - [dim]arxiv.org/abs/1711.05101[/dim]\n', delay: 300 },
    { text: '[yellow bold]● THE REVIEWER (REVIEWER)[/yellow bold] Auditing hypothesis novelty & theoretical rigor...\n  Peer Review Assessment: [green bold]APPROVED (Score: 8.8/10)[/green bold]\n', delay: 350 },
    { text: '[green bold]● THE CODER (CODER)[/green bold] Generating experiment.py with reproducibility seeds...\n', delay: 250 },
    { text: '[cyan bold]● EXECUTION SANDBOX[/cyan bold] Running experiment.py in isolated sandbox...\n', delay: 300 },
    { text: '  Duration: 0.84s | Return Code: 0\n  Parsed Metrics:\n    • adamw_final_loss: 0.00342\n    • lion_final_loss: 0.00189\n    • lion_speedup: 1.48x\n', delay: 200 },
    { text: '[magenta bold]● THE SYNTHESIZER (SYNTHESIZER)[/magenta bold] Compiling scientific artifacts...\n  ✔ Generated plot.py & rendered plot.png\n  ✔ Drafted academic LaTeX manuscript (paper.tex)\n  ✔ Compiled publication PDF: paper.pdf\n  ✔ Compiled Markdown report: report.md\n', delay: 350 },
    { text: '\n[green bold]✔ Research completed successfully. All artifacts saved to experiments/adamw_vs_lion_20260904/[/green bold]\n', delay: 100 }
  ],
  paper: [
    { text: 'xavier paper experiments/sparse_attention --open', delay: 40, isInput: true },
    { text: '\n[bold cyan]Research Paper Artifacts (sparse_attention)[/bold cyan]\n', delay: 150 },
    { text: '┌──────────────────┬────────────┬──────────────────────────────────────────┐\n│ Format           │ Status     │ File Path                                │\n├──────────────────┼────────────┼──────────────────────────────────────────┤\n│ Publication PDF  │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/paper.pdf   │\n│ Academic HTML    │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/paper.html  │\n│ LaTeX Source     │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/paper.tex   │\n│ Markdown Report  │ [green bold]Ready[/green bold]      │ experiments/sparse_attention/report.md   │\n└──────────────────┴────────────┴──────────────────────────────────────────┘\n', delay: 200 },
    { text: '[green bold]✔ Opening paper.pdf in default viewer...[/green bold]\n', delay: 150 }
  ],
  history: [
    { text: 'xavier history', delay: 40, isInput: true },
    { text: '\n[bold cyan]XavierLabs AI Research History[/bold cyan]\n', delay: 150 },
    { text: '┌────┬──────────────────┬────────────────────────────────────────┬───────────┬───────────┐\n│ ID │ Date             │ Topic                                  │ Status    │ Artifacts │\n├────┼──────────────────┼────────────────────────────────────────┼───────────┼───────────┤\n│ 3  │ 2026-09-04 00:15 │ Sparse attention scaling on sequences  │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 2  │ 2026-09-03 23:42 │ Convergence of AdamW vs Lion optimizer │ [green bold]COMPLETED[/green bold] │ 6 files   │\n│ 1  │ 2026-09-03 21:10 │ Monte Carlo estimation benchmarks      │ [green bold]COMPLETED[/green bold] │ 5 files   │\n└────┴──────────────────┴────────────────────────────────────────┴───────────┴───────────┘\n', delay: 200 }
  ],
  config: [
    { text: 'xavier config', delay: 40, isInput: true },
    { text: '\n[bold cyan]XavierLabs AI Configuration & Compute Telemetry[/bold cyan]\n', delay: 150 },
    { text: '┌───────────────────────────┬─────────────────────────────────────────────────┐\n│ Component                 │ Configured Value                                │\n├───────────────────────────┼─────────────────────────────────────────────────┤\n│ Execution Sandbox         │ Local Isolated Subprocess Sandbox (Fallback)    │\n│ Ideator Model             │ gemini/gemini-2.5-flash                         │\n│ Reviewer Model            │ gemini/gemini-2.5-flash (or ollama/deepseek-r1)  │\n│ Coder Model               │ gemini/gemini-2.5-flash                         │\n│ Synthesizer Model         │ gemini/gemini-2.5-flash                         │\n│ Max Debug Retries         │ 3                                               │\n│ Database Engine           │ SQLite (xavierlabs.db)                          │\n└───────────────────────────┴─────────────────────────────────────────────────┘\n', delay: 200 }
  ]
};

let terminalIsTyping = false;

function initTerminal() {
  const termBody = document.getElementById('terminalBody');
  const pills = document.querySelectorAll('.pill-cmd');

  // Load initial research demo
  runTerminalDemo('research');

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      if (terminalIsTyping) return;
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const cmd = pill.dataset.cmd;
      runTerminalDemo(cmd);
    });
  });
}

function runTerminalDemo(cmdKey) {
  const termBody = document.getElementById('terminalBody');
  if (!termBody || terminalIsTyping) return;

  terminalIsTyping = true;
  termBody.innerHTML = `<div class="term-pixel-logo">${escapeHtml(PIXEL_BANNER.trim())}</div>\n`;

  const script = DEMO_SCRIPTS[cmdKey] || DEMO_SCRIPTS['research'];
  let stepIndex = 0;

  function nextStep() {
    if (stepIndex >= script.length) {
      termBody.innerHTML += `\n<div class="term-prompt-line"><span class="term-prompt">xavier@lab:~$</span> <span class="cursor-blink"></span></div>`;
      termBody.scrollTop = termBody.scrollHeight;
      terminalIsTyping = false;
      return;
    }

    const item = script[stepIndex];
    stepIndex++;

    if (item.isInput) {
      const promptDiv = document.createElement('div');
      promptDiv.className = 'term-prompt-line';
      promptDiv.innerHTML = `<span class="term-prompt">xavier@lab:~$</span> <span class="typed-input"></span><span class="cursor-blink"></span>`;
      termBody.appendChild(promptDiv);

      const targetSpan = promptDiv.querySelector('.typed-input');
      const cursor = promptDiv.querySelector('.cursor-blink');
      let charIdx = 0;

      const typeInterval = setInterval(() => {
        if (charIdx < item.text.length) {
          targetSpan.textContent += item.text[charIdx];
          charIdx++;
          termBody.scrollTop = termBody.scrollHeight;
        } else {
          clearInterval(typeInterval);
          cursor.remove();
          setTimeout(nextStep, 250);
        }
      }, 25);
    } else {
      const formatted = formatTerminalTags(item.text);
      termBody.innerHTML += formatted;
      termBody.scrollTop = termBody.scrollHeight;
      setTimeout(nextStep, item.delay || 150);
    }
  }

  nextStep();
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

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}
