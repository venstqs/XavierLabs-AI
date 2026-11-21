(function () {
  var repo = 'https://github.com/venstqs/XavierLabs-AI.git';
  var commands = {
    pip: 'pip install git+' + repo,
    uv: 'uv pip install git+' + repo,
    git: 'git clone ' + repo + ' && cd XavierLabs-AI && pip install -e .'
  };
  var current = 'pip';
  var cmdEl = document.getElementById('installCmd');

  document.querySelectorAll('.tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      document.querySelectorAll('.tab').forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      current = tab.dataset.tab;
      cmdEl.textContent = commands[current];
    });
  });

  var copyBtn = document.getElementById('copyBtn');
  copyBtn.addEventListener('click', function () {
    var text = commands[current];
    var done = function () {
      copyBtn.setAttribute('aria-label', 'Copied');
      copyBtn.style.color = 'var(--fg)';
      setTimeout(function () { copyBtn.setAttribute('aria-label', 'Copy install command'); copyBtn.style.color = ''; }, 1500);
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

  // Draw the block-character logo as SVG squares so it renders crisply in any font.
  var logo = document.querySelector('.logo');
  if (logo) {
    var rows = logo.textContent.split('\n');
    var cols = Math.max.apply(null, rows.map(function (r) { return r.length; }));
    var rects = '';
    rows.forEach(function (row, y) {
      for (var x = 0; x < row.length; x++) {
        if (row[x] === '█') rects += '<rect x="' + x + '" y="' + y + '" width="0.86" height="0.86"/>';
      }
    });
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 ' + cols + ' ' + rows.length);
    svg.setAttribute('class', 'logo-svg');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'xavierlabs');
    svg.innerHTML = rects;
    logo.replaceWith(svg);
  }

  document.getElementById('themeToggle').addEventListener('click', function () {
    var next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) { /* ignore */ }
  });
})();
