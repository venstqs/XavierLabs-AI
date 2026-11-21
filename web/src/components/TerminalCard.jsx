import { useEffect, useState } from 'react';
import SpotlightCard from './rb/SpotlightCard.jsx';

const LINES = [
  { cls: 'b', text: 'xavier research "does Lion beat AdamW on Rastrigin?"', type: true },
  { cls: 'd', text: 'found 4 papers on ArXiv and Semantic Scholar' },
  { cls: 'b', text: 'hypothesis  Lion reaches lower loss at equal steps' },
  { cls: 'g', text: 'review      approved, 8.6 / 10' },
  { cls: 'd', text: 'writing experiment.py' },
  { cls: 'r', text: 'run 1       failed: shape (64,) vs (32,)' },
  { cls: 'd', text: 'reading traceback, patching experiment.py' },
  { cls: 'g', text: 'run 2       passed in 0.84s' },
  { cls: 'b', text: 'lion 0.00189   adamw 0.00342   1.48x faster' },
  { cls: 'g', text: 'paper.pdf   report.md   plot.png   ready' }
];

export default function TerminalCard({ theme }) {
  const [rendered, setRendered] = useState([]);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      setRendered(
        LINES.map(l => ({
          cls: l.cls,
          text: (l.type ? '$ ' : '  ') + l.text
        }))
      );
      setDone(true);
      return;
    }

    let cancelled = false;
    let timer = null;

    const play = () => {
      if (cancelled) return;
      setRendered([]);
      setDone(false);

      let lineIdx = 0;

      const nextLine = () => {
        if (cancelled) return;
        if (lineIdx >= LINES.length) {
          setDone(true);
          timer = setTimeout(play, 6000);
          return;
        }

        const item = LINES[lineIdx++];
        if (item.type) {
          let charIdx = 0;
          setRendered([{ cls: 'b', text: '$ ' }]);

          const typeChar = () => {
            if (cancelled) return;
            if (charIdx < item.text.length) {
              charIdx += 1;
              const slice = item.text.slice(0, charIdx);
              setRendered([{ cls: 'b', text: `$ ${slice}` }]);
              timer = setTimeout(typeChar, 22 + Math.random() * 28);
            } else {
              timer = setTimeout(nextLine, 400);
            }
          };

          timer = setTimeout(typeChar, 120);
        } else {
          setRendered(prev => [...prev, { cls: item.cls, text: `  ${item.text}` }]);
          timer = setTimeout(nextLine, 520);
        }
      };

      nextLine();
    };

    play();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, []);

  return (
    <SpotlightCard
      className="term-card"
      theme={theme}
      intensity={theme === 'dark' ? 0.14 : 0.1}
      borderGlow={theme === 'dark' ? 0.55 : 0.45}
      spotlightSize={280}
    >
      <div className="term-top">
        <span />
        <span />
        <span />
        <em>xavier research</em>
      </div>
      <pre className="term-body" aria-label="Live xavier research terminal session">
        {rendered.map((line, i) => (
          <span key={i} className={line.cls}>
            {line.text}
            {'\n'}
          </span>
        ))}
        {done && <span className="caret" aria-hidden="true" />}
      </pre>
    </SpotlightCard>
  );
}
