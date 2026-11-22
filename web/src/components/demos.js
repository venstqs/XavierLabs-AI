// Terminal demo scripts. They mirror the real `xavier` CLI output.
// Markup: [b]bold [d]dim [g]accent [r]red [y]yellow [l]line-gray, closed by [/].

const rule = (idx, name) => {
  const head = `${idx}  ${name} `;
  return `[d]${idx}[/]  [b]${name}[/] [l]${'─'.repeat(Math.max(4, 60 - head.length))}[/]`;
};

const strip = (s) => s.replace(/\[(\/|[bdgryl])\]/g, '');

const box = (title, lines, color) => {
  const width = 60;
  const top = `[${color}]╭─[/] ${title} [${color}]${'─'.repeat(Math.max(1, width - strip(title).length - 5))}╮[/]`;
  const body = lines.map((ln) => `[${color}]│[/] ${ln}${' '.repeat(Math.max(0, width - strip(ln).length - 4))} [${color}]│[/]`);
  const bottom = `[${color}]╰${'─'.repeat(width - 2)}╯[/]`;
  return [top, ...body, bottom].join('\n');
};

export const BANNER =
  '[b]  ╱╲ [/]  [b]XavierLabs[/]\n' +
  '[b] ╱──╲[/]  [d]autonomous computational research[/]\n' +
  '[b]╱    ╲[/] [b]●[/][d] ready · v0.1.0[/]\n';

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
        '[l]│[/]  [d]model    [/] [b]groq/llama-3.3-70b-versatile[/]             [l]│[/]\n' +
        '[l]│[/]  [d]sandbox  [/] Docker Container                         [l]│[/]\n' +
        '[l]╰────────────────────────────────────────────────────╯[/]\n' +
        '[d]Describe a topic to brainstorm, [b]/research <topic>[/] to run the swarm, or [b]/help[/].[/]\n',
      d: 450,
    },
    { chat: '/help' },
    {
      out:
        '[b]Commands[/]\n' +
        ' [d]Command             Description[/]\n' +
        ' [l]────────────────────────────────────────────────────[/]\n' +
        ' /research <topic>   Launch autonomous research loop\n' +
        ' /paper [folder]     Inspect or open a compiled paper\n' +
        ' /history            Browse past experiment records\n' +
        ' /model [name]       Switch model or provider\n' +
        ' /config             Show model, keys and sandbox\n',
      d: 500,
    },
    { chat: 'can sparse top-k attention reduce gradient variance?' },
    {
      out:
        '\nPlausibly. Restricting each query to its top-k keys removes low-weight\n' +
        'terms from the softmax Jacobian, so per-step gradient noise should fall\n' +
        'as [b]k[/] shrinks, until too few keys starve the signal.\n\n' +
        '[b]Launch an autonomous research run on this topic now?[/] [d][Y/n][/]: y\n',
      d: 500,
    },
    { out: '\n[b]▶ Launching research swarm:[/] sparse top-k attention & gradient variance\n', d: 300 },
  ],
  research: [
    { cmd: 'xavier research "AdamW vs Lion on non-convex loss surfaces"' },
    { out: '\n' + BANNER, d: 250 },
    { out: '[d]Sandbox[/]  Docker Container (xavierlabs-sandbox:latest)\n', d: 300 },
    { out: '\n' + rule('01', 'Ideator') + '\n[b]●[/] Querying literature & formulating hypothesis...', d: 700 },
    {
      out:
        '\nRetrieved 4 publications\n' +
        '  • Symbolic Discovery of Optimization Algorithms [d](2023)[/]\n' +
        '  • Decoupled Weight Decay Regularization [d](2019)[/]\n' +
        '[d]Hypothesis[/]  [b]Lion reaches lower loss than AdamW on Rastrigin[/]\n',
      d: 600,
    },
    { out: '\n' + rule('02', 'Reviewer') + '\n[b]●[/] Conducting rigorous peer review...\n', d: 700 },
    {
      out:
        '[b]Peer review · approved[/]\n' +
        ' [d]Novelty[/]       8.5  [b]━━━━━━━━[/][l]━━[/]\n' +
        ' [d]Rigor[/]         8.0  [b]━━━━━━━━[/][l]━━[/]\n' +
        ' [d]Feasibility[/]   9.0  [b]━━━━━━━━━[/][l]━[/]\n' +
        ' [b]Overall      8.6[/]  [b]━━━━━━━━━[/][l]━[/]\n',
      d: 500,
    },
    { out: '\n' + rule('03', 'Coder') + '\n[b]●[/] Synthesizing computational experiment (experiment.py)...\n', d: 800 },
    { out: '\n' + rule('04', 'Execution Sandbox') + '\n[b]●[/] Executing experiment in isolated sandbox (Attempt #1)...\n', d: 700 },
    { out: box('[r]●[/] [b]Run #1[/] [d]failed · exit 1 · 0.41s[/]', ['[r]ValueError: operands could not be broadcast[/]', '[r]together with shapes (64,) (32,)[/]'], 'r') + '\n', d: 600 },
    { out: '\n' + rule('03', 'Coder') + '\n[b]●[/] Auto-debugging: reading the traceback and patching experiment.py...\n', d: 900 },
    { out: '\n' + rule('04', 'Execution Sandbox') + '\n[b]●[/] Executing experiment in isolated sandbox (Attempt #2)...\n', d: 700 },
    { out: box('[b]●[/] [b]Run #2[/] [d]passed · 0.84s · docker_container[/]', ['[d]adamw_final_loss[/]  0.00342', '[d]lion_final_loss [/]  0.00189', '[d]lion_speedup    [/]  1.48'], 'l') + '\n', d: 600 },
    { out: '\n' + rule('05', 'Synthesizer') + '\n[b]●[/] Synthesizing figures, LaTeX paper, and research report...\n', d: 700 },
    { out: '[b]✔[/] Rendered plot.png\n[b]✔[/] Generated paper.tex\n[b]✔[/] Generated report.md\n[b]✔[/] Compiled paper.pdf\n', d: 500 },
    { out: '\n[d]Artifacts in experiments/adamw-vs-lion_20261122_031500/[/]\n', d: 200 },
  ],
  paper: [
    { cmd: 'xavier paper experiments/sparse-attention_20261121 --open' },
    {
      out:
        '\n[b]Research Paper Artifacts (sparse-attention_20261121)[/]\n\n' +
        ' [d]Format            Status   File[/]\n' +
        ' [l]────────────────────────────────────────────────[/]\n' +
        ' Publication PDF   [b]Ready[/]    paper.pdf\n' +
        ' Academic HTML     [b]Ready[/]    paper.html\n' +
        ' LaTeX Source      [b]Ready[/]    paper.tex\n' +
        ' Markdown Report   [b]Ready[/]    report.md\n',
      d: 500,
    },
    { out: '\n[b]Opening paper.pdf...[/]\n', d: 200 },
  ],
  history: [
    { cmd: 'xavier history' },
    {
      out:
        '\n[b]Research History[/]\n\n' +
        ' [d]ID  Date              Topic                          Status[/]\n' +
        ' [l]────────────────────────────────────────────────────────────[/]\n' +
        ' 4   2026-11-21 19:08  Sparse top-k attention         [b]COMPLETED[/]\n' +
        ' 3   2026-11-20 22:41  AdamW vs Lion on Rastrigin     [b]COMPLETED[/]\n' +
        ' 2   2026-11-20 21:10  A vague idea about "AI"        [d]REJECTED[/]\n' +
        ' 1   2026-11-19 18:02  Monte Carlo pi convergence     [b]COMPLETED[/]\n',
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
        ' Execution Sandbox     [b]Docker Container (xavierlabs-sandbox)[/]\n' +
        ' Active/Auto Model     [b]groq/llama-3.3-70b-versatile[/]\n' +
        ' Max Debug Retries     3\n' +
        ' Execution Timeout     180s\n' +
        ' GROQ_API_KEY          [b]Detected[/]\n' +
        ' OPENROUTER_API_KEY    [d]Not set[/]\n' +
        ' OLLAMA_API_BASE       http://localhost:11434\n',
      d: 500,
    },
  ],
};
