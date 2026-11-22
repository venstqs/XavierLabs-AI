// Terminal demo scripts mirroring the real `xavier` CLI output with VS Code syntax tokens.
// Markup: [b]bold [d]dim [g]teal-type [r]red [y]fn-yellow [c]var-blue [s]str-coral [p]flag-purple [n]num-mint [l]line-gray, closed by [/].

const rule = (idx, name) => {
  const head = `${idx}  ${name} `;
  return `[p]${idx}[/]  [y]${name}[/] [l]${'─'.repeat(Math.max(4, 60 - head.length))}[/]`;
};

const strip = (s) => s.replace(/\[(\/|[bdgrycspnl])\]/g, '');

const box = (title, lines, color) => {
  const width = 60;
  const top = `[${color}]╭─[/] ${title} [${color}]${'─'.repeat(Math.max(1, width - strip(title).length - 5))}╮[/]`;
  const body = lines.map((ln) => `[${color}]│[/] ${ln}${' '.repeat(Math.max(0, width - strip(ln).length - 4))} [${color}]│[/]`);
  const bottom = `[${color}]╰${'─'.repeat(width - 2)}╯[/]`;
  return [top, ...body, bottom].join('\n');
};

export const BANNER =
  '[c]  ╱╲ [/]  [b]XavierLabs[/]\n' +
  '[c] ╱──╲[/]  [d]autonomous computational research[/]\n' +
  '[c]╱    ╲[/] [g]●[/][d] ready · [/][n]v0.1.0[/]\n';

export const TABS = [
  { value: 'chat', label: 'xavier chat' },
  { value: 'research', label: 'xavier research' },
  { value: 'paper', label: 'xavier paper' },
  { value: 'history', label: 'xavier history' },
  { value: 'config', label: 'xavier config' },
];

export const DEMOS = {
  chat: [
    { cmd: 'xavier' },
    { out: '\n' + BANNER, d: 250 },
    {
      out:
        '[l]╭────────────────────────────────────────────────────╮[/]\n' +
        '[l]│[/]  [c]model    [/] [s]groq/llama-3.3-70b-versatile[/]             [l]│[/]\n' +
        '[l]│[/]  [c]sandbox  [/] [g]Docker Container[/]                         [l]│[/]\n' +
        '[l]╰────────────────────────────────────────────────────╯[/]\n' +
        '[d]Describe a topic to brainstorm, [/][y]/research[/] [s]<topic>[/][d] to run the swarm, or [/][y]/help[/][d].[/]\n',
      d: 450,
    },
    { chat: '/help' },
    {
      out:
        '[b]Commands[/]\n' +
        ' [d]Command             Description[/]\n' +
        ' [l]────────────────────────────────────────────────────[/]\n' +
        ' [y]/research[/] [s]<topic>[/]   Launch autonomous research loop\n' +
        ' [y]/paper[/] [s][folder][/]     Inspect or open a compiled paper\n' +
        ' [y]/history[/]            Browse past experiment records\n' +
        ' [y]/model[/] [s][name][/]       Switch model or provider\n' +
        ' [y]/config[/]             Show model, keys and sandbox\n',
      d: 500,
    },
    { chat: 'can sparse top-k attention reduce gradient variance?' },
    {
      out:
        '\nPlausibly. Restricting each query to its [c]top-k[/] keys removes low-weight\n' +
        'terms from the softmax Jacobian, so per-step gradient noise should fall\n' +
        'as [c]k[/] shrinks, until too few keys starve the signal.\n\n' +
        '[y]Launch an autonomous research run on this topic now?[/] [d][Y/n][/]: [g]y[/]\n',
      d: 500,
    },
    { out: '\n[g]▶[/] [b]Launching research swarm:[/] [s]sparse top-k attention & gradient variance[/]\n', d: 300 },
  ],
  research: [
    { cmd: 'xavier research "AdamW vs Lion on non-convex loss surfaces"' },
    { out: '\n' + BANNER, d: 250 },
    { out: '[c]Sandbox[/]  [g]Docker Container[/] [d](xavierlabs-sandbox:latest)[/]\n', d: 300 },
    { out: '\n' + rule('01', 'Ideator') + '\n[c]●[/] Querying literature & formulating hypothesis...', d: 700 },
    {
      out:
        '\nRetrieved [n]4[/] publications\n' +
        '  • [s]Symbolic Discovery of Optimization Algorithms[/] [d](2023)[/]\n' +
        '  • [s]Decoupled Weight Decay Regularization[/] [d](2019)[/]\n' +
        '[c]Hypothesis[/]  [b]Lion reaches lower loss than AdamW on Rastrigin[/]\n',
      d: 600,
    },
    { out: '\n' + rule('02', 'Reviewer') + '\n[c]●[/] Conducting rigorous peer review...\n', d: 700 },
    {
      out:
        '[b]Peer review · [/][g]approved[/]\n' +
        ' [c]Novelty[/]       [n]8.5[/]  [g]━━━━━━━━[/][l]━━[/]\n' +
        ' [c]Rigor[/]         [n]8.0[/]  [g]━━━━━━━━[/][l]━━[/]\n' +
        ' [c]Feasibility[/]   [n]9.0[/]  [g]━━━━━━━━━[/][l]━[/]\n' +
        ' [b]Overall      [/][n]8.6[/]  [y]━━━━━━━━━[/][l]━[/]\n',
      d: 500,
    },
    { out: '\n' + rule('03', 'Coder') + '\n[c]●[/] Synthesizing computational experiment ([s]experiment.py[/])...\n', d: 800 },
    { out: '\n' + rule('04', 'Execution Sandbox') + '\n[c]●[/] Executing experiment in isolated sandbox (Attempt [n]#1[/])...\n', d: 700 },
    { out: box('[r]●[/] [b]Run #1[/] [d]failed · exit 1 · [/][n]0.41s[/]', ['[r]ValueError: operands could not be broadcast[/]', '[r]together with shapes (64,) (32,)[/]'], 'r') + '\n', d: 600 },
    { out: '\n' + rule('03', 'Coder') + '\n[y]●[/] Auto-debugging: reading traceback and patching [s]experiment.py[/]...\n', d: 900 },
    { out: '\n' + rule('04', 'Execution Sandbox') + '\n[c]●[/] Executing experiment in isolated sandbox (Attempt [n]#2[/])...\n', d: 700 },
    { out: box('[g]●[/] [b]Run #2[/] [d]passed · [/][n]0.84s[/][d] · docker_container[/]', ['[c]adamw_final_loss[/]  [n]0.00342[/]', '[c]lion_final_loss [/]  [n]0.00189[/]', '[c]lion_speedup    [/]  [n]1.48x[/]'], 'l') + '\n', d: 600 },
    { out: '\n' + rule('05', 'Synthesizer') + '\n[c]●[/] Synthesizing figures, LaTeX paper, and research report...\n', d: 700 },
    { out: '[g]✔[/] Rendered [s]plot.png[/]\n[g]✔[/] Generated [s]paper.tex[/]\n[g]✔[/] Generated [s]report.md[/]\n[g]✔[/] Compiled [s]paper.pdf[/]\n', d: 500 },
    { out: '\n[d]Artifacts in [/][s]experiments/adamw-vs-lion_20261122_031500/[/]\n', d: 200 },
  ],
  paper: [
    { cmd: 'xavier paper experiments/sparse-attention_20261121 --open' },
    {
      out:
        '\n[b]Research Paper Artifacts[/] [d]([/][s]sparse-attention_20261121[/][d])[/]\n\n' +
        ' [d]Format            Status   File[/]\n' +
        ' [l]────────────────────────────────────────────────[/]\n' +
        ' Publication PDF   [g]Ready[/]    [s]paper.pdf[/]\n' +
        ' Academic HTML     [g]Ready[/]    [s]paper.html[/]\n' +
        ' LaTeX Source      [g]Ready[/]    [s]paper.tex[/]\n' +
        ' Markdown Report   [g]Ready[/]    [s]report.md[/]\n',
      d: 500,
    },
    { out: '\n[c]Opening[/] [s]paper.pdf[/]...\n', d: 200 },
  ],
  history: [
    { cmd: 'xavier history' },
    {
      out:
        '\n[b]Research History[/]\n\n' +
        ' [d]ID  Date              Topic                          Status[/]\n' +
        ' [l]────────────────────────────────────────────────────────────[/]\n' +
        ' [n]4[/]   2026-11-21 19:08  [s]Sparse top-k attention[/]         [g]COMPLETED[/]\n' +
        ' [n]3[/]   2026-11-20 22:41  [s]AdamW vs Lion on Rastrigin[/]     [g]COMPLETED[/]\n' +
        ' [n]2[/]   2026-11-20 21:10  [s]A vague idea about "AI"[/]        [y]REJECTED[/]\n' +
        ' [n]1[/]   2026-11-19 18:02  [s]Monte Carlo pi convergence[/]     [g]COMPLETED[/]\n',
      d: 500,
    },
  ],
  config: [
    { cmd: 'xavier config' },
    {
      out:
        '\n[b]Configuration[/]\n\n' +
        ' [d]Component             Value[/]\n' +
        ' [l]──────────────────────────────────────────────────────[/]\n' +
        ' [c]Execution Sandbox[/]     [g]Docker Container[/] [d](xavierlabs-sandbox)[/]\n' +
        ' [c]Active/Auto Model[/]     [s]groq/llama-3.3-70b-versatile[/]\n' +
        ' [c]Max Debug Retries[/]     [n]3[/]\n' +
        ' [c]Execution Timeout[/]     [n]180s[/]\n' +
        ' [c]GROQ_API_KEY[/]          [g]Detected[/]\n' +
        ' [c]OPENROUTER_API_KEY[/]    [d]Not set[/]\n' +
        ' [c]OLLAMA_API_BASE[/]       [s]http://localhost:11434[/]\n',
      d: 500,
    },
  ],
};
