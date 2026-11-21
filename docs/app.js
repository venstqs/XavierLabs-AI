(function () {
  // ---------------------------------------------------------------- install listing
  var repo = 'https://github.com/venstqs/XavierLabs-AI.git';
  var commands = {
    pip: 'pip install git+' + repo,
    uv: 'uv pip install git+' + repo,
    git: 'git clone ' + repo + ' && cd XavierLabs-AI && pip install -e .'
  };
  var current = 'pip';
  var cmdEl = document.getElementById('installCmd');
  var tabs = document.querySelectorAll('.tab');

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      current = tab.dataset.tab;
      cmdEl.textContent = commands[current];
    });
  });

  var copyBtn = document.getElementById('copyBtn');
  copyBtn.addEventListener('click', function () {
    var text = commands[current];
    var done = function () {
      copyBtn.textContent = 'Copied';
      setTimeout(function () { copyBtn.textContent = 'Copy'; }, 1500);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done);
    } else {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { /* ignore */ }
      document.body.removeChild(ta);
    }
  });

  // ---------------------------------------------------------------- theme
  var themeBtn = document.getElementById('themeToggle');
  var label = function () { themeBtn.textContent = document.documentElement.dataset.theme === 'dark' ? 'Light' : 'Dark'; };
  label();
  themeBtn.addEventListener('click', function () {
    var next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) { /* ignore */ }
    label();
  });

  // ---------------------------------------------------------------- Figure 2
  var svg = document.getElementById('plot');
  if (!svg) return;
  var NS = 'http://www.w3.org/2000/svg';
  var W = 560, H = 300, L = 62, R = 18, T = 16, B = 46;
  var steps = 2000, yMax = 1.0;
  var x = function (s) { return L + (s / steps) * (W - L - R); };
  var y = function (v) { return T + (1 - v / yMax) * (H - T - B); };

  // deterministic noise so the figure is identical on every load
  var seed = 7;
  var rand = function () { seed = (seed * 16807) % 2147483647; return seed / 2147483647 - 0.5; };
  var curve = function (rate, floor, wiggle) {
    var d = '';
    for (var s = 0; s <= steps; s += 20) {
      var v = floor + (1 - floor) * Math.exp(-rate * s) + wiggle * Math.exp(-s / 900) * rand();
      d += (s === 0 ? 'M' : 'L') + x(s).toFixed(1) + ' ' + y(Math.max(0, Math.min(yMax, v))).toFixed(1);
    }
    return d;
  };
  var el = function (tag, attrs, text) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text) n.textContent = text;
    svg.appendChild(n);
    return n;
  };

  [0.25, 0.5, 0.75].forEach(function (v) { el('line', { class: 'grid', x1: L, x2: W - R, y1: y(v), y2: y(v) }); });
  el('path', { class: 'axis', d: 'M' + L + ' ' + T + ' V' + (H - B) + ' H' + (W - R) });
  [0, 500, 1000, 1500, 2000].forEach(function (s) {
    el('line', { class: 'axis', x1: x(s), x2: x(s), y1: H - B, y2: H - B + 5 });
    el('text', { class: 'tick', x: x(s), y: H - B + 20, 'text-anchor': 'middle' }, s.toLocaleString('en-US'));
  });
  [0, 0.5, 1].forEach(function (v) {
    el('line', { class: 'axis', x1: L - 5, x2: L, y1: y(v), y2: y(v) });
    el('text', { class: 'tick', x: L - 10, y: y(v) + 4, 'text-anchor': 'end' }, v.toFixed(1));
  });
  el('text', { class: 'label', x: (L + W - R) / 2, y: H - 6, 'text-anchor': 'middle' }, 'step');
  el('text', { class: 'label', x: 16, y: (T + H - B) / 2, 'text-anchor': 'middle', transform: 'rotate(-90 16 ' + (T + H - B) / 2 + ')' }, 'loss');

  var adamw = el('path', { class: 'curve adamw', d: curve(0.0021, 0.0034, 0.06) });
  var lion = el('path', { class: 'curve lion', d: curve(0.0032, 0.0019, 0.06) });

  // legend
  var lx = W - R - 132, ly = T + 10;
  el('rect', { class: 'legend', x: lx, y: ly, width: 122, height: 50 });
  el('line', { class: 'curve adamw', x1: lx + 10, x2: lx + 38, y1: ly + 17, y2: ly + 17 });
  el('text', { class: 'tick', x: lx + 46, y: ly + 21 }, 'AdamW');
  el('line', { class: 'curve lion', x1: lx + 10, x2: lx + 38, y1: ly + 35, y2: ly + 35 });
  el('text', { class: 'tick', x: lx + 46, y: ly + 39 }, 'Lion');

  // The one moment of motion: the curves draw themselves once, when the figure is reached.
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced || !('IntersectionObserver' in window)) return;
  var prep = function (path, dashed) {
    var len = path.getTotalLength();
    path.style.strokeDasharray = dashed ? '' : len;
    if (!dashed) path.style.strokeDashoffset = len;
    path.style.opacity = dashed ? '0' : '1';
    return len;
  };
  prep(adamw, false);
  prep(lion, true);
  var io = new IntersectionObserver(function (entries) {
    if (!entries[0].isIntersecting) return;
    io.disconnect();
    adamw.style.transition = 'stroke-dashoffset 1.4s ease-out';
    adamw.style.strokeDashoffset = '0';
    lion.style.transition = 'opacity 0.9s ease-out 0.9s';
    lion.style.opacity = '1';
  }, { threshold: 0.5 });
  io.observe(svg);
})();
