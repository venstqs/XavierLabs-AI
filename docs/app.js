(function () {
  'use strict';
  var REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s) { return document.querySelector(s); };
  var $$ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };

  // ---------------------------------------------------------------- theme
  $$('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) { /* ignore */ }
      var meta = $('meta[name="theme-color"]');
      if (meta) meta.setAttribute('content', next === 'dark' ? '#0a0a0a' : '#ffffff');
      if (waves) waves.recolor();
    });
  });

  // ---------------------------------------------------------------- rotating word pill
  var words = ['reads the literature', 'tests a hypothesis', 'runs real experiments', 'fixes its own bugs', 'writes the paper'];
  var pill = $('#wordPill');
  if (pill && !REDUCED) {
    var wi = 0;
    setInterval(function () {
      pill.classList.add('out');
      setTimeout(function () {
        wi = (wi + 1) % words.length;
        pill.textContent = words[wi];
        pill.classList.remove('out');
      }, 260);
    }, 2400);
  }

  // ---------------------------------------------------------------- tags strip
  var TAGS = ['ArXiv', 'Semantic Scholar', 'LiteLLM', 'Groq', 'DeepSeek', 'OpenRouter', 'Ollama', 'Gemini',
    'Docker', 'NumPy', 'SciPy', 'Matplotlib', 'SQLite', 'LaTeX'];
  var track = $('#tags');
  if (track) {
    TAGS.concat(TAGS).forEach(function (t, i) {
      var el = document.createElement('span');
      el.className = 'tag';
      el.textContent = t;
      if (i >= TAGS.length) el.setAttribute('aria-hidden', 'true');
      track.appendChild(el);
    });
  }

  // ---------------------------------------------------------------- install
  var repo = 'https://github.com/venstqs/XavierLabs-AI.git';
  var cmds = { pip: 'pip install git+' + repo, uv: 'uv pip install git+' + repo, git: 'git clone ' + repo + ' && cd XavierLabs-AI && pip install -e .' };
  var current = 'pip';
  $$('.seg-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      $$('.seg-btn').forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      current = b.dataset.tab;
      $('#installCmd').textContent = cmds[current];
    });
  });
  var copyBtn = $('#copyBtn');
  copyBtn.addEventListener('click', function () {
    var text = cmds[current];
    var done = function () {
      copyBtn.style.borderColor = 'var(--live)';
      copyBtn.setAttribute('aria-label', 'Copied');
      setTimeout(function () { copyBtn.style.borderColor = ''; copyBtn.setAttribute('aria-label', 'Copy install command'); }, 1400);
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done);
    else {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { /* ignore */ }
      document.body.removeChild(ta);
    }
  });

  // ---------------------------------------------------------------- pill nav: highlight current section
  var links = $$('.pill-nav a');
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    ['about', 'how', 'install'].forEach(function (id) { var el = document.getElementById(id); if (el) spy.observe(el); });
  }

  // ---------------------------------------------------------------- terminal card: replays a run
  var LINES = [
    ['$ ', 'xavier research "does Lion beat AdamW on Rastrigin?"', 'type'],
    ['d', 'found 4 papers on ArXiv and Semantic Scholar'],
    ['b', 'hypothesis  Lion reaches lower loss at equal steps'],
    ['g', 'review      approved, 8.6 / 10'],
    ['d', 'writing experiment.py'],
    ['r', 'run 1       failed: shape (64,) vs (32,)'],
    ['d', 'reading traceback, patching experiment.py'],
    ['g', 'run 2       passed in 0.84s'],
    ['b', 'lion 0.00189   adamw 0.00342   1.48x faster'],
    ['g', 'paper.pdf   report.md   plot.png   ready'],
  ];
  var term = $('#term');
  function line(cls, text) {
    var s = document.createElement('span');
    s.className = cls;
    s.textContent = text + '\n';
    term.appendChild(s);
  }
  function play() {
    term.textContent = '';
    if (REDUCED) {
      LINES.forEach(function (l) { line(l[0] === '$ ' ? 'b' : l[0], (l[0] === '$ ' ? '$ ' : '  ') + l[1]); });
      return;
    }
    var i = 0;
    (function next() {
      if (i >= LINES.length) {
        var c = document.createElement('span'); c.className = 'caret'; term.appendChild(c);
        setTimeout(play, 6000);
        return;
      }
      var l = LINES[i++];
      if (l[2] === 'type') {
        var s = document.createElement('span'); s.className = 'b'; s.textContent = '$ ';
        term.appendChild(s);
        var k = 0;
        (function type() {
          if (k < l[1].length) { s.textContent += l[1][k++]; setTimeout(type, 22 + Math.random() * 30); }
          else { s.textContent += '\n'; setTimeout(next, 400); }
        })();
      } else {
        line(l[0], '  ' + l[1]);
        setTimeout(next, 520);
      }
    })();
  }
  if (term) play();

  // ---------------------------------------------------------------- flowing lines (hero background)
  var waves = null;
  (function () {
    var canvas = $('#waves');
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var w = 0, h = 0, t = 0, raf = 0, visible = true, ink = '245,245,245';
    var STRANDS = 38;
    function readInk() {
      var hex = (getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#f5f5f5').replace('#', '');
      if (hex.length === 3) hex = hex.split('').map(function (x) { return x + x; }).join('');
      var n = parseInt(hex, 16);
      ink = [(n >> 16) & 255, (n >> 8) & 255, n & 255].join(',');
    }
    function resize() {
      var r = canvas.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = r.width; h = r.height;
      canvas.width = Math.max(1, Math.round(w * dpr));
      canvas.height = Math.max(1, Math.round(h * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }
    function draw() {
      ctx.clearRect(0, 0, w, h);
      // keep the strands to the right of the headline on wide screens
      var startX = w > 980 ? w * 0.42 : w * 0.3;
      for (var i = 0; i < STRANDS; i++) {
        var p = i / (STRANDS - 1);
        ctx.strokeStyle = 'rgba(' + ink + ',' + (0.03 + 0.12 * Math.sin(p * Math.PI)).toFixed(3) + ')';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (var x = startX; x <= w + 8; x += 8) {
          var u = (x - startX) / (w - startX || 1);
          var y = h * (0.82 - 0.5 * u)
            + Math.sin(u * 5 + t + p * 1.8) * h * (0.08 + 0.14 * u) * (0.55 + 0.45 * p)
            + Math.cos(u * 2.1 - t * 0.6 + p * 3.1) * h * 0.03
            + (p - 0.5) * h * 0.24 * u;
          if (x === startX) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
    }
    function loop() {
      if (!visible) { raf = 0; return; }
      t += 0.004;
      draw();
      raf = requestAnimationFrame(loop);
    }
    readInk();
    resize();
    window.addEventListener('resize', resize);
    if (!REDUCED && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (e) {
        visible = e[0].isIntersecting;
        if (visible && !raf) raf = requestAnimationFrame(loop);
      }).observe(canvas);
    }
    waves = { recolor: function () { readInk(); draw(); } };
  })();
})();
