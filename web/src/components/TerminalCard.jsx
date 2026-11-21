import { useEffect, useState } from 'react';
import SpotlightCard from './rb/SpotlightCard.jsx';

const LINES = [
  { cls: 'b', text: 'xavier research "does Lion beat AdamW on Rastrigin?"', type: true, stage: 0 },
  { cls: 'd', text: '[literature]  4 papers indexed from ArXiv & Semantic Scholar', stage: 1 },
  { cls: 'b', text: '[hypothesis]  Lion reaches lower loss at equal step budget', stage: 1 },
  { cls: 'g', text: '[reviewer]    approved · score 8.6 / 10 (novelty 8.8, rigor 8.4)', stage: 2 },
  { cls: 'd', text: '[coder]       generating experiment.py (NumPy + SciPy)', stage: 3 },
  { cls: 'r', text: '[sandbox]     run 1 failed: ValueError shape (64,) vs (32,)', stage: 3 },
  { cls: 'd', text: '[debugger]    inspecting traceback, patching update step...', stage: 3 },
  { cls: 'g', text: '[sandbox]     run 2 passed in 0.84s (exit 0)', stage: 4 },
  { cls: 'b', text: '[metrics]     lion 0.00189 · adamw 0.00342 · 1.48x faster', stage: 4 },
  { cls: 'g', text: '[writer]      compiled paper.pdf, paper.tex, report.md, plot.png', stage: 5 }
];

const ARTIFACTS = [
  { name: 'literature.json', detail: '4 citations', unlockStage: 1 },
  { name: 'review.json', detail: '8.6 / 10 pass', unlockStage: 2 },
  { name: 'experiment.py', detail: 'auto-patched · 0.84s', unlockStage: 4 },
  { name: 'plot.png', detail: 'loss curves', unlockStage: 5 },
  { name: 'paper.pdf', detail: 'LaTeX + PDF + HTML', unlockStage: 5 }
];

export default function TerminalCard({ theme }) {
  const [rendered, setRendered] = useState([]);
  const [stage, setStage] = useState(0);
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
      setStage(5);
      setDone(true);
      return;
    }

    let cancelled = false;
    let timer = null;

    const play = () => {
      if (cancelled) return;
      setRendered([]);
      setStage(0);
      setDone(false);

      let lineIdx = 0;

      const nextLine = () => {
        if (cancelled) return;
        if (lineIdx >= LINES.length) {
          setDone(true);
          timer = setTimeout(play, 6500);
          return;
        }

        const item = LINES[lineIdx++];
        setStage(item.stage);

        if (item.type) {
          let charIdx = 0;
          setRendered([{ cls: 'b', text: '$ ' }]);

          const typeChar = () => {
            if (cancelled) return;
            if (charIdx < item.text.length) {
              charIdx += 1;
              setRendered([{ cls: 'b', text: `$ ${item.text.slice(0, charIdx)}` }]);
              timer = setTimeout(typeChar, 20 + Math.random() * 24);
            } else {
              timer = setTimeout(nextLine, 380);
            }
          };

          timer = setTimeout(typeChar, 140);
        } else {
          setRendered(prev => [...prev, { cls: item.cls, text: `  ${item.text}` }]);
          timer = setTimeout(nextLine, 540);
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
      className="workbench"
      theme={theme}
      intensity={theme === 'dark' ? 0.1 : 0.06}
      borderGlow={theme === 'dark' ? 0.45 : 0.35}
      spotlightSize={360}
    >
      <div className="workbench-bar">
        <div className="workbench-dots" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        <span className="workbench-title">xavier research — session #042</span>
        <span className={`workbench-status${done ? ' is-done' : ''}`}>
          <i />
          {done ? 'complete' : 'running'}
        </span>
      </div>

      <div className="workbench-grid">
        <pre className="workbench-term" aria-label="Live xavier research terminal session">
          {rendered.map((line, i) => (
            <span key={i} className={line.cls}>
              {line.text}
              {'\n'}
            </span>
          ))}
          {done && <span className="caret" aria-hidden="true" />}
        </pre>

        <aside className="workbench-side" aria-label="Generated run artifacts">
          <div className="workbench-side-head">
            <span>RUN ARTIFACTS</span>
            <span>{ARTIFACTS.filter(a => stage >= a.unlockStage).length}/{ARTIFACTS.length}</span>
          </div>
          <ul className="artifact-list">
            {ARTIFACTS.map(art => {
              const ready = stage >= art.unlockStage;
              return (
                <li key={art.name} className={ready ? 'is-ready' : ''}>
                  <span className="artifact-dot" />
                  <div className="artifact-meta">
                    <code>{art.name}</code>
                    <span>{ready ? art.detail : 'pending…'}</span>
                  </div>
                </li>
              );
            })}
          </ul>
        </aside>
      </div>
    </SpotlightCard>
  );
}
