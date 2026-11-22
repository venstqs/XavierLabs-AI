import { useEffect, useRef, useState } from 'react';
import { motion, useInView, useReducedMotion } from 'motion/react';
import PillTabs from './PillTabs.jsx';
import { DEMOS, TABS } from './demos.js';

const CLASS = { b: 't-b', d: 't-d', g: 't-g', r: 't-r', y: 't-y', l: 't-l' };

/** Turns the demo markup into React nodes (text is never parsed as HTML). */
function Markup({ src }) {
  const root = [];
  const stack = [root];
  const re = /\[(\/|[bdgryl])\]/g;
  let last = 0;
  let m;
  let key = 0;
  while ((m = re.exec(src))) {
    if (m.index > last) stack[stack.length - 1].push(src.slice(last, m.index));
    if (m[1] === '/') {
      if (stack.length > 1) {
        const children = stack.pop();
        const cls = children.cls;
        stack[stack.length - 1].push(<span key={key++} className={cls}>{children}</span>);
      }
    } else {
      const children = [];
      children.cls = CLASS[m[1]];
      stack.push(children);
    }
    last = re.lastIndex;
  }
  if (last < src.length) stack[stack.length - 1].push(src.slice(last));
  while (stack.length > 1) {
    const children = stack.pop();
    stack[stack.length - 1].push(<span key={key++} className={children.cls}>{children}</span>);
  }
  return <>{root}</>;
}

const PROMPTS = { cmd: '[b]xavier@lab[/]:[d]~[/]$ ', chat: '\n[b]xavier[/] [d]›[/] ' };

export default function Terminal() {
  const [tab, setTab] = useState('chat');
  const [blocks, setBlocks] = useState([]);
  const [finished, setFinished] = useState(false);
  const wrapRef = useRef(null);
  const bodyRef = useRef(null);
  const inView = useInView(wrapRef, { once: true, amount: 0.3 });
  const reduced = useReducedMotion();

  useEffect(() => {
    if (!inView) return undefined;
    let cancelled = false;
    const timers = [];
    const wait = (ms) => new Promise((res) => timers.push(setTimeout(res, reduced ? 0 : ms)));

    setBlocks([]);
    setFinished(false);

    (async () => {
      for (const step of DEMOS[tab]) {
        if (cancelled) return;
        const kind = step.cmd ? 'cmd' : step.chat ? 'chat' : null;
        if (kind) {
          const text = step.cmd || step.chat;
          setBlocks((b) => [...b, { prefix: PROMPTS[kind], typed: '', typing: true }]);
          for (let i = 1; i <= text.length; i++) {
            if (cancelled) return;
            if (!reduced) await wait(16 + Math.random() * 24);
            setBlocks((b) => {
              const next = b.slice();
              next[next.length - 1] = { ...next[next.length - 1], typed: text.slice(0, reduced ? text.length : i) };
              return next;
            });
            if (reduced) break;
          }
          setBlocks((b) => {
            const next = b.slice();
            next[next.length - 1] = { ...next[next.length - 1], typing: false };
            return next;
          });
          await wait(260);
        } else {
          setBlocks((b) => [...b, { out: step.out }]);
          await wait(step.d || 200);
        }
      }
      if (!cancelled) setFinished(true);
    })();

    return () => {
      cancelled = true;
      timers.forEach(clearTimeout);
    };
  }, [tab, inView, reduced]);

  useEffect(() => {
    const el = bodyRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [blocks, finished]);

  return (
    <motion.div
      ref={wrapRef}
      className="terminal-wrapper"
      id="demo"
      initial={{ opacity: 0, y: 24, scale: 0.98 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="terminal-header">
        <div className="terminal-dots" aria-hidden="true"><span /><span /><span /></div>
        <PillTabs
          items={TABS}
          value={tab}
          onChange={setTab}
          layoutId="term-tab"
          className="terminal-tabs"
          tabClassName="term-tab"
          label="Demo command"
        />
      </div>
      <pre className="terminal-body" ref={bodyRef} aria-live="polite">
        {blocks.map((b, i) =>
          b.out !== undefined ? (
            <Markup key={i} src={b.out} />
          ) : (
            <span key={i}>
              <Markup src={b.prefix} />
              <span className="t-b">{b.typed}</span>
              {b.typing && <span className="cursor-blink" />}
              {!b.typing && '\n'}
            </span>
          )
        )}
        {finished && (
          <span>
            {'\n'}
            <Markup src={PROMPTS.cmd} />
            <span className="cursor-blink" />
          </span>
        )}
      </pre>
    </motion.div>
  );
}
