// XavierLabs AI: landing page interactions
(function () {
  'use strict';

  var REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var REPO = 'https://github.com/venstqs/XavierLabs-AI.git';

  var INSTALL = {
    pip: 'pip install git+' + REPO,
    uv: 'uv pip install git+' + REPO,
    git: 'git clone ' + REPO + ' && cd XavierLabs-AI && pip install -e .'
  };

  var TOOLS = ['ArXiv', 'Semantic Scholar', 'LiteLLM', 'Groq', 'DeepSeek', 'OpenRouter', 'Ollama', 'Gemini',
    'Docker', 'NumPy', 'SciPy', 'Matplotlib', 'Seaborn', 'SQLite', 'LaTeX', 'MathJax', 'Typer', 'Rich'];

  // ------------------------------------------------------------------ helpers
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function toast(msg) {
    var el = $('#toast');
    if (!el) return;
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.classList.remove('show'); }, 2000);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () { legacyCopy(text); });
    }
    legacyCopy(text);
    return Promise.resolve();
  }

  function legacyCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
  }

  // ------------------------------------------------------------------ theme
  function currentTheme() { return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'; }

  function initTheme() {
    $all('[data-theme-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var next = currentTheme() === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        try { localStorage.setItem('theme', next); } catch (e) { /* ignore */ }
        var meta = $('meta[name="theme-color"]');
        if (meta) meta.setAttribute('content', next === 'dark' ? '#0a0a0a' : '#ffffff');
        if (waves) waves.recolor();
      });
    });
  }

  // ------------------------------------------------------------------ flowing lines (hero)
  var waves = null;

  function initWaves() {
    var canvas = $('#waves');
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var w = 0, h = 0, dpr = 1, t = 0, raf = 0, visible = true, ink = '10,10,10';
    var STRANDS = 34;

    function readInk() {
      var c = getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#0a0a0a';
      var hex = c.replace('#', '');
      if (hex.length === 3) hex = hex.split('').map(function (x) { return x + x; }).join('');
      var n = parseInt(hex, 16);
      ink = [(n >> 16) & 255, (n >> 8) & 255, n & 255].join(',');
    }

    function resize() {
      var rect = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = rect.width; h = rect.height;
      canvas.width = Math.max(1, Math.round(w * dpr));
      canvas.height = Math.max(1, Math.round(h * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      var startX = w * 0.18;
      for (var i = 0; i < STRANDS; i++) {
        var p = i / (STRANDS - 1);
        var alpha = 0.035 + 0.13 * Math.sin(p * Math.PI);
        ctx.strokeStyle = 'rgba(' + ink + ',' + alpha.toFixed(3) + ')';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (var x = startX; x <= w + 8; x += 8) {
          var u = (x - startX) / (w - startX || 1);
          var amp = h * (0.10 + 0.16 * u);
          var y = h * (0.78 - 0.42 * u)
            + Math.sin(u * 5.2 + t + p * 1.8) * amp * (0.55 + 0.45 * p)
            + Math.cos(u * 2.1 - t * 0.6 + p * 3.1) * h * 0.035
            + (p - 0.5) * h * 0.22 * u;
          if (x === startX) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
    }

    function loop() {
      if (!visible) { raf = 0; return; }
      t += 0.0045;
      draw();
      raf = requestAnimationFrame(loop);
    }

    readInk();
    resize();
    window.addEventListener('resize', resize);

    if (!REDUCED && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible && !raf) raf = requestAnimationFrame(loop);
      }).observe(canvas);
    }

    waves = { recolor: function () { readInk(); draw(); } };
  }

  // ------------------------------------------------------------------ install + copy
  function initInstall() {
    var code = $('#installCode');
    var active = 'pip';
    $all('[data-install]').forEach(function (tab) {
      tab.addEventListener('click', function () {
        $all('[data-install]').forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        active = tab.dataset.install;
        code.innerHTML = '';
        var ps = document.createElement('span');
        ps.className = 'prompt';
        ps.textContent = '$';
        code.appendChild(ps);
        code.appendChild(document.createTextNode(INSTALL[active]));
      });
    });

    $all('[data-copy]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var key = btn.dataset.copy;
        var text = key === 'install' ? INSTALL[active] : ($('#' + key) || {}).textContent || '';
        if (!text) return;
        copyText(text.trim()).then(function () {
          var label = btn.textContent;
          btn.textContent = 'Copied';
          toast('Copied to clipboard');
          setTimeout(function () { btn.textContent = label; }, 1600);
        });
      });
    });
  }

  // ------------------------------------------------------------------ tools marquee
  function initTools() {
    var track = $('#toolsTrack');
    if (!track) return;
    var list = TOOLS.concat(TOOLS); // duplicated for a seamless loop
    list.forEach(function (name, i) {
      var el = document.createElement('span');
      el.className = 'tool';
      el.textContent = name;
      if (i >= TOOLS.length) el.setAttribute('aria-hidden', 'true');
      track.appendChild(el);
    });
  }

  // ------------------------------------------------------------------ terminal demo
  // Markup: [b]bold [d]dim [g]green [r]red [y]yellow [l]rule-gray, closed by [/].
  var RULE = function (idx, name) {
    var head = idx + '  ' + name + ' ';
    return '[d]' + idx + '[/]  [b]' + name + '[/] [l]' + new Array(Math.max(4, 62 - head.length)).join('─') + '[/]';
  };
  var BANNER =
    '[b]  ╱╲ [/]  [b]XavierLabs[/]\n' +
    '[b] ╱──╲[/]  [d]autonomous computational research[/]\n' +
    '[b]╱    ╲[/] [g]●[/][d] ready · v0.1.0[/]\n';
  function box(title, lines, color) {
    var width = 62;
    var top = '[' + color + ']╭─[/] ' + title + ' [' + color + ']' + new Array(Math.max(2, width - stripTags(title).length - 3)).join('─') + '╮[/]';
    var body = lines.map(function (ln) {
      var pad = width - stripTags(ln).length - 2;
      return '[' + color + ']│[/] ' + ln + new Array(Math.max(1, pad + 1)).join(' ') + '[' + color + ']│[/]';
    });
    var bottom = '[' + color + ']╰' + new Array(width).join('─') + '╯[/]';
    return [top].concat(body, [bottom]).join('\n');
  }
  function stripTags(s) { return s.replace(/\[(\/|[bdgryl])\]/g, ''); }

  var DEMOS = {
    research: [
      { cmd: 'xavier research "AdamW vs Lion on non-convex loss surfaces"' },
      { out: '\n' + BANNER, d: 250 },
      { out: '[d]Sandbox[/]  Docker Container (xavierlabs-sandbox:latest)\n', d: 300 },
      { out: '\n' + RULE('01', 'Ideator') + '\n[g]●[/] Querying literature & formulating hypothesis...', d: 700 },
      { out: '\nRetrieved 4 publications\n  • Symbolic Discovery of Optimization Algorithms [d](2023)[/]\n  • Decoupled Weight Decay Regularization [d](2019)[/]\n[d]Hypothesis[/]  [b]Lion reaches lower loss than AdamW on Rastrigin at equal budgets[/]\n', d: 600 },
      { out: '\n' + RULE('02', 'Reviewer') + '\n[g]●[/] Conducting rigorous peer review...\n', d: 700 },
      { out: '[b]Peer review · [g]approved[/][/]\n [d]Novelty[/]       8.5  [b]━━━━━━━━[/][l]━━[/]\n [d]Rigor[/]         8.0  [b]━━━━━━━━[/][l]━━[/]\n [d]Feasibility[/]   9.0  [b]━━━━━━━━━[/][l]━[/]\n [b]Overall      8.6[/]  [b]━━━━━━━━━[/][l]━[/]\n', d: 500 },
      { out: '\n' + RULE('03', 'Coder') + '\n[g]●[/] Synthesizing computational experiment (experiment.py)...\n', d: 800 },
      { out: '\n' + RULE('04', 'Execution Sandbox') + '\n[g]●[/] Executing experiment in isolated sandbox (Attempt #1)...\n', d: 700 },
      { out: box('[r]●[/] [b]Run #1[/] [d]failed · exit 1 · 0.41s[/]', ['[r]ValueError: operands could not be broadcast[/]', '[r]together with shapes (64,) (32,)[/]'], 'r') + '\n', d: 600 },
      { out: '\n' + RULE('03', 'Coder') + '\n[g]●[/] Auto-debugging: reading the traceback and patching experiment.py...\n', d: 900 },
      { out: '\n' + RULE('04', 'Execution Sandbox') + '\n[g]●[/] Executing experiment in isolated sandbox (Attempt #2)...\n', d: 700 },
      { out: box('[g]●[/] [b]Run #2[/] [d]passed · 0.84s · docker_container[/]', ['[d]adamw_final_loss[/]  0.00342', '[d]lion_final_loss [/]  0.00189', '[d]lion_speedup    [/]  1.48'], 'l') + '\n', d: 600 },
      { out: '\n' + RULE('05', 'Synthesizer') + '\n[g]●[/] Synthesizing figures, LaTeX paper, and research report...\n', d: 700 },
      { out: '[g]✔[/] Rendered plot.png\n[g]✔[/] Generated paper.tex\n[g]✔[/] Generated report.md\n[g]✔[/] Compiled paper.pdf\n', d: 500 },
      { out: '\n[d]Artifacts in experiments/adamw-vs-lion_20261122_031500/[/]\n', d: 200 }
    ],
    chat: [
      { cmd: 'xavier' },
      { out: '\n' + BANNER, d: 250 },
      { out: '[l]╭──────────────────────────────────────────────────────╮[/]\n[l]│[/]  [d]model    [/] [b]groq/llama-3.3-70b-versatile[/]               [l]│[/]\n[l]│[/]  [d]sandbox  [/] Docker Container                           [l]│[/]\n[l]╰──────────────────────────────────────────────────────╯[/]\n[d]Describe a topic to brainstorm, [b]/research <topic>[/] to run the swarm, or [b]/help[/].[/]\n', d: 400 },
      { chat: 'can sparse top-k attention reduce gradient variance?' },
      { out: '\nPlausibly. Restricting each query to its top-k keys removes low-weight\nterms from the softmax Jacobian, so per-step gradient noise should fall as\n[b]k[/] shrinks, until too few keys starve the signal.\n\nA quick test: a 2-layer transformer on synthetic copy tasks, sweeping\nk ∈ {4, 8, 16, full}, logging gradient-norm variance over 2k steps.\n\n[g]Launch an autonomous research run on this topic now?[/] [d][Y/n][/]: y\n', d: 500 },
      { out: '\n[b]▶ Launching research swarm:[/] sparse top-k attention & gradient variance\n', d: 300 }
    ],
    paper: [
      { cmd: 'xavier paper experiments/sparse-attention_20261121 --open' },
      { out: '\n[b]Research Paper Artifacts (sparse-attention_20261121)[/]\n\n [d]Format            Status   File[/]\n [l]──────────────────────────────────────────────────────[/]\n Publication PDF   [g]Ready[/]    paper.pdf\n Academic HTML     [g]Ready[/]    paper.html\n LaTeX Source      [g]Ready[/]    paper.tex\n Markdown Report   [g]Ready[/]    report.md\n', d: 500 },
      { out: '\n[g]Opening paper.pdf...[/]\n', d: 200 }
    ],
    history: [
      { cmd: 'xavier history' },
      { out: '\n[b]Research History[/]\n\n [d]ID  Date              Topic                            Status[/]\n [l]──────────────────────────────────────────────────────────────[/]\n 4   2026-11-21 19:08  Sparse top-k attention variance  [g]COMPLETED[/]\n 3   2026-11-20 22:41  AdamW vs Lion on Rastrigin       [g]COMPLETED[/]\n 2   2026-11-20 21:10  Vague idea about “AI”            [y]REJECTED[/]\n 1   2026-11-19 18:02  Monte Carlo pi convergence       [g]COMPLETED[/]\n', d: 500 }
    ],
    config: [
      { cmd: 'xavier config' },
      { out: '\n[b]Configuration[/]\n\n [d]Component             Value[/]\n [l]──────────────────────────────────────────────────────────[/]\n Execution Sandbox     [b]Docker Container (xavierlabs-sandbox:latest)[/]\n Active/Auto Model     [b]groq/llama-3.3-70b-versatile[/]\n Max Debug Retries     3\n Execution Timeout     180s\n GROQ_API_KEY          [g]Detected[/]\n OPENROUTER_API_KEY    [d]Not set[/]\n OLLAMA_API_BASE       http://localhost:11434\n', d: 500 }
    ]
  };

  var CLASS = { b: 't-b', d: 't-d', g: 't-g', r: 't-r', y: 't-y', l: 't-line' };

  // Safe renderer: builds DOM nodes with textContent, never innerHTML.
  function renderMarkup(src) {
    var frag = document.createDocumentFragment();
    var stack = [frag];
    var re = /\[(\/|[bdgryl])\]/g, last = 0, m;
    while ((m = re.exec(src))) {
      if (m.index > last) stack[stack.length - 1].appendChild(document.createTextNode(src.slice(last, m.index)));
      if (m[1] === '/') {
        if (stack.length > 1) stack.pop();
      } else {
        var span = document.createElement('span');
        span.className = CLASS[m[1]];
        stack[stack.length - 1].appendChild(span);
        stack.push(span);
      }
      last = re.lastIndex;
    }
    if (last < src.length) stack[stack.length - 1].appendChild(document.createTextNode(src.slice(last)));
    return frag;
  }

  var demoToken = 0;
  var demoTimer = null;

  function runDemo(key) {
    var body = $('#terminalBody');
    if (!body) return;
    var token = ++demoToken;
    clearTimeout(demoTimer);
    body.textContent = '';
    var steps = DEMOS[key] || DEMOS.research;
    var i = 0;

    function scroll() { body.scrollTop = body.scrollHeight; }

    function typeLine(prefix, text, done) {
      var line = document.createElement('span');
      line.appendChild(renderMarkup(prefix));
      var typed = document.createElement('span');
      typed.className = 't-b';
      var cursor = document.createElement('span');
      cursor.className = 'cursor';
      line.appendChild(typed);
      line.appendChild(cursor);
      body.appendChild(line);
      if (REDUCED) { typed.textContent = text; cursor.remove(); body.appendChild(document.createTextNode('\n')); return done(); }
      var c = 0;
      (function tick() {
        if (token !== demoToken) return;
        if (c < text.length) {
          typed.textContent += text[c++];
          scroll();
          demoTimer = setTimeout(tick, 18 + Math.random() * 22);
        } else {
          cursor.remove();
          body.appendChild(document.createTextNode('\n'));
          demoTimer = setTimeout(done, 260);
        }
      })();
    }

    function next() {
      if (token !== demoToken) return;
      if (i >= steps.length) {
        body.appendChild(renderMarkup('\n[d]~/research[/] [b]$[/] '));
        var cur = document.createElement('span');
        cur.className = 'cursor';
        body.appendChild(cur);
        scroll();
        return;
      }
      var s = steps[i++];
      if (s.cmd) return typeLine('[d]~/research[/] [b]$[/] ', s.cmd, next);
      if (s.chat) return typeLine('[b]xavier[/] [d]›[/] ', s.chat, next);
      body.appendChild(renderMarkup(s.out));
      scroll();
      demoTimer = setTimeout(next, REDUCED ? 0 : (s.d || 200));
    }

    next();
  }

  function initTerminal() {
    var tabs = $all('.term-tab');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
        runDemo(tab.dataset.cmd);
      });
    });

    var term = $('.terminal');
    if (!term) return;
    if ('IntersectionObserver' in window) {
      var started = false;
      new IntersectionObserver(function (entries, obs) {
        if (entries[0].isIntersecting && !started) {
          started = true;
          runDemo('research');
          obs.disconnect();
        }
      }, { threshold: 0.25 }).observe(term);
    } else {
      runDemo('research');
    }
  }

  // ------------------------------------------------------------------ nav: scrolled state + scroll spy
  function initNav() {
    var navwrap = $('#navwrap');
    function onScroll() { if (navwrap) navwrap.classList.toggle('scrolled', window.scrollY > 8); }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    if (!('IntersectionObserver' in window)) return;
    var links = $all('[data-spy]');
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.toggle('active', a.dataset.spy === e.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach(function (a) {
      var section = document.getElementById(a.dataset.spy);
      if (section) spy.observe(section);
    });
  }

  // ------------------------------------------------------------------ reveal on scroll
  function initReveal() {
    var els = $all('.reveal');
    if (REDUCED || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  }

  // ------------------------------------------------------------------ boot
  function init() {
    var year = $('#year');
    if (year) year.textContent = String(new Date().getFullYear());
    initTheme();
    initWaves();
    initInstall();
    initTools();
    initTerminal();
    initNav();
    initReveal();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
