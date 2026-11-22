import { useEffect, useRef } from 'react';

/**
 * Interactive dot grid (canvas). Dots near the cursor grow, brighten and get
 * pushed away, then spring back. Colors follow the --dot theme token.
 */
export default function DotGrid({ gap = 26, radius = 1.1, reach = 130, push = 14 }) {
  const ref = useRef(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas.getContext('2d');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let dots = [];
    let w = 0;
    let h = 0;
    let raf = 0;
    let visible = true;
    const mouse = { x: -9999, y: -9999 };

    const readColor = () =>
      getComputedStyle(document.documentElement).getPropertyValue('--dot').trim() || '245,245,245';
    let rgb = readColor();

    const build = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = rect.width;
      h = rect.height;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      dots = [];
      const ox = (w % gap) / 2;
      const oy = (h % gap) / 2;
      for (let y = oy; y < h; y += gap) {
        for (let x = ox; x < w; x += gap) dots.push({ bx: x, by: y, x, y, vx: 0, vy: 0 });
      }
    };

    const frame = () => {
      ctx.clearRect(0, 0, w, h);
      for (const d of dots) {
        const dx = d.bx - mouse.x;
        const dy = d.by - mouse.y;
        const dist = Math.hypot(dx, dy);
        const k = dist < reach ? 1 - dist / reach : 0;
        const tx = d.bx + (dist ? (dx / dist) * push * k : 0);
        const ty = d.by + (dist ? (dy / dist) * push * k : 0);
        d.vx = (d.vx + (tx - d.x) * 0.12) * 0.78;
        d.vy = (d.vy + (ty - d.y) * 0.12) * 0.78;
        d.x += d.vx;
        d.y += d.vy;
        ctx.fillStyle = `rgba(${rgb},${(0.14 + 0.55 * k).toFixed(3)})`;
        ctx.beginPath();
        ctx.arc(d.x, d.y, radius + 1.4 * k, 0, Math.PI * 2);
        ctx.fill();
      }
      raf = visible && !reduced ? requestAnimationFrame(frame) : 0;
    };

    const onMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
      if (!raf && visible && !reduced) raf = requestAnimationFrame(frame);
    };
    const onLeave = () => { mouse.x = mouse.y = -9999; };
    const onResize = () => { build(); frame(); };

    const themeObserver = new MutationObserver(() => { rgb = readColor(); if (!raf) frame(); });
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

    const io = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible && !raf && !reduced) raf = requestAnimationFrame(frame);
    });
    io.observe(canvas);

    build();
    frame();
    window.addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('pointerleave', onLeave);
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(raf);
      themeObserver.disconnect();
      io.disconnect();
      window.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerleave', onLeave);
      window.removeEventListener('resize', onResize);
    };
  }, [gap, radius, reach, push]);

  return (
    <div className="dot-grid" aria-hidden="true">
      <canvas ref={ref} />
    </div>
  );
}
