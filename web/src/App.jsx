import { useCallback, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useScroll, useSpring } from 'motion/react';
import DotGrid from './components/DotGrid.jsx';
import DecryptedText from './components/DecryptedText.jsx';
import BlurText from './components/BlurText.jsx';
import PillTabs from './components/PillTabs.jsx';
import SpotlightCard from './components/SpotlightCard.jsx';
import Terminal from './components/Terminal.jsx';

const REPO = 'https://github.com/venstqs/XavierLabs-AI';
const INSTALL = {
  pip: `pip install git+${REPO}.git`,
  uv: `uv pip install git+${REPO}.git`,
  git: `git clone ${REPO}.git && cd XavierLabs-AI && pip install -e .`,
};
const INSTALL_TABS = [
  { value: 'pip', label: 'pip' },
  { value: 'uv', label: 'uv' },
  { value: 'git', label: 'git clone' },
];

const FEATURES = [
  {
    idx: '01 // DISCOVERY',
    title: 'Literature & Hypothesis',
    body: 'Queries ArXiv and Semantic Scholar without paid API keys. Identifies open gaps in computational research and formulates mathematically testable hypotheses.',
  },
  {
    idx: '02 // PEER REVIEW',
    title: 'Adversarial Audit',
    body: 'Simulates an expert peer reviewer to critique mathematical soundness and feasibility before code runs. Scores proposals from 1 to 10 and sends weak ones back for revision.',
  },
  {
    idx: '03 // CONTAINMENT',
    title: 'Sandboxed Auto-Debugger',
    body: 'Runs generated simulations in an offline Docker container or a locked-down local sandbox. When code crashes, it reads the traceback and rewrites the script.',
  },
  {
    idx: '04 // SIMULATION',
    title: 'Empirical Verification',
    body: (
      <>
        Writes self-contained scientific Python simulations (NumPy, SciPy). Fixes deterministic seeds and saves hard
        computed results to <code>metrics.json</code>.
      </>
    ),
  },
  {
    idx: '05 // SYNTHESIS',
    title: 'Publication-Ready Papers',
    body: (
      <>
        Renders 300-DPI figures and compiles complete manuscripts: <code>paper.tex</code>, <code>paper.pdf</code>,{' '}
        <code>paper.html</code> and Markdown.
      </>
    ),
  },
  {
    idx: '06 // MULTI-MODEL',
    title: 'Universal Model Support',
    body: 'Connect Groq for fast inference, DeepSeek for mathematical reasoning, OpenRouter for 100+ models, or run fully offline with local Ollama.',
  },
];

const COMMANDS = [
  ['xavier', 'Start the interactive research console'],
  ['xavier research "Your research inquiry"', 'Run the autonomous end-to-end loop'],
  ['xavier research "..." --force', 'Run even if the Reviewer rejects the hypothesis'],
  ['xavier paper experiments/your_folder --open', 'View and open the compiled PDF / LaTeX paper'],
  ['xavier history', 'Browse the audit trail of past experiments'],
  ['xavier config', 'Inspect the active model, detected API keys and sandbox'],
];

const QUICKSTART = [
  ['# 1. Install the CLI', `pip install git+${REPO}.git`],
  ['# 2. Connect a model provider (Groq, DeepSeek, OpenRouter, or Ollama)', 'xavier auth'],
  ['# 3. Launch the interactive console', 'xavier'],
  ['# 4. Or run a one-liner autonomous research loop', 'xavier research "Analyze AdamW vs Lion optimizer on non-convex loss functions"'],
  ['# 5. View and open the compiled research paper', 'xavier paper experiments/your_experiment_folder --open'],
];

function GitHubIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M12 2C6.48 2 2 6.48 2 12.02c0 4.43 2.87 8.18 6.84 9.5.5.09.68-.22.68-.48l-.01-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.95 0-1.09.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.03A9.56 9.56 0 0 1 12 6.84c.85 0 1.7.12 2.5.34 1.91-1.3 2.75-1.03 2.75-1.03.55 1.38.2 2.4.1 2.65.64.7 1.03 1.6 1.03 2.69 0 3.85-2.34 4.7-4.57 4.94.36.31.68.92.68 1.86l-.01 2.75c0 .27.18.58.69.48A10.02 10.02 0 0 0 22 12.02C22 6.48 17.52 2 12 2Z" />
    </svg>
  );
}

function ThemeToggle() {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme || 'dark');
  const toggle = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('xl-theme', next); } catch { /* storage unavailable */ }
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', next === 'dark' ? '#000000' : '#ffffff');
    setTheme(next);
  };
  return (
    <button type="button" className="theme-btn" onClick={toggle} aria-label="Toggle color theme">
      <AnimatePresence mode="wait" initial={false}>
        <motion.svg
          key={theme}
          width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"
          initial={{ rotate: -90, opacity: 0, scale: 0.6 }}
          animate={{ rotate: 0, opacity: 1, scale: 1 }}
          exit={{ rotate: 90, opacity: 0, scale: 0.6 }}
          transition={{ duration: 0.2 }}
          aria-hidden="true"
        >
          {theme === 'dark' ? (
            <g><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></g>
          ) : (
            <path strokeLinejoin="round" d="M20.5 14.1A8.5 8.5 0 0 1 9.9 3.5a8.5 8.5 0 1 0 10.6 10.6Z" />
          )}
        </motion.svg>
      </AnimatePresence>
    </button>
  );
}

function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); } catch { /* ignore */ }
  document.body.removeChild(ta);
  return Promise.resolve();
}

function CopyButton({ text, onCopied }) {
  const [copied, setCopied] = useState(false);
  const timer = useRef(0);
  const click = () => {
    copyText(text).then(() => {
      setCopied(true);
      onCopied?.(text);
      clearTimeout(timer.current);
      timer.current = setTimeout(() => setCopied(false), 1600);
    });
  };
  return (
    <motion.button type="button" className="btn-copy" onClick={click} whileTap={{ scale: 0.94 }} aria-label="Copy command">
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={copied ? 'done' : 'copy'}
          initial={{ y: 6, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -6, opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          {copied ? '✓ Copied' : 'Copy'}
        </motion.span>
      </AnimatePresence>
    </motion.button>
  );
}

/** Code block whose lines slide in one after another when scrolled into view. */
function WorkflowBox({ id, title, children }) {
  return (
    <motion.section
      className="workflow-box"
      id={id}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-60px' }}
      variants={{ hidden: { opacity: 0, y: 18 }, show: { opacity: 1, y: 0, transition: { duration: 0.5, staggerChildren: 0.05, delayChildren: 0.15 } } }}
    >
      <div className="workflow-header">{title}</div>
      <div className="workflow-code">{children}</div>
    </motion.section>
  );
}

const lineVariants = { hidden: { opacity: 0, x: -8 }, show: { opacity: 1, x: 0, transition: { duration: 0.35 } } };
const Line = ({ className, children }) => (
  <motion.span className={`line${className ? ` ${className}` : ''}`} variants={lineVariants}>{children}</motion.span>
);

export default function App() {
  const [installTab, setInstallTab] = useState('pip');
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(0);
  const { scrollYProgress } = useScroll();
  const progress = useSpring(scrollYProgress, { stiffness: 140, damping: 30, mass: 0.3 });

  const showToast = useCallback((text) => {
    setToast(`Copied: "${text.length > 34 ? `${text.slice(0, 34)}...` : text}"`);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2200);
  }, []);

  useEffect(() => () => clearTimeout(toastTimer.current), []);

  return (
    <>
      <motion.div className="scroll-progress" style={{ scaleX: progress }} aria-hidden="true" />
      <DotGrid />

      <header>
        <div className="container header-inner">
          <a href="#" className="pixel-logo" aria-label="xavierlabs home">xavierlabs</a>
          <nav className="header-nav" aria-label="Main">
            <a href="#demo">demo</a>
            <a href="#features">features</a>
            <a href="#commands">commands</a>
            <a href="#quickstart">quickstart</a>
            <ThemeToggle />
            <a href={REPO} target="_blank" rel="noopener noreferrer" className="btn-github-nav">
              <GitHubIcon />
              <span>GitHub</span>
            </a>
          </nav>
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <DecryptedText text="xavierlabs" className="hero-brand-name" />
          <BlurText text="Terminal-native computational scientific research engine." className="hero-headline" delay={0.35} />
          <motion.p
            className="hero-subtext"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.5 }}
          >
            From literature review to compiled LaTeX papers, in one command.
          </motion.p>

          <motion.div
            className="install-container"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.05, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          >
            <PillTabs
              items={INSTALL_TABS}
              value={installTab}
              onChange={setInstallTab}
              layoutId="install-tab"
              className="pill-tabs"
              tabClassName="pill-tab"
              label="Install method"
            />
            <div className="install-box">
              <code className="install-code">
                <span className="prompt">$</span>
                <AnimatePresence mode="wait" initial={false}>
                  <motion.span
                    key={installTab}
                    initial={{ opacity: 0, y: 6, filter: 'blur(4px)' }}
                    animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                    exit={{ opacity: 0, y: -6, filter: 'blur(4px)' }}
                    transition={{ duration: 0.18 }}
                  >
                    {INSTALL[installTab]}
                  </motion.span>
                </AnimatePresence>
              </code>
              <CopyButton text={INSTALL[installTab]} onCopied={showToast} />
            </div>
            <div className="install-meta">Python 3.10+ · macOS, Linux, Windows · MIT License</div>
          </motion.div>

          <Terminal />
        </section>

        <section className="features-grid" id="features">
          {FEATURES.map((f, i) => (
            <SpotlightCard key={f.idx} className="feature-col" index={i}>
              <div className="feature-idx">{f.idx}</div>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </SpotlightCard>
          ))}
        </section>

        <WorkflowBox id="commands" title="// CLI COMMANDS & WORKFLOW">
          {COMMANDS.map(([cmd, note]) => (
            <Line key={cmd}>
              <span className="cmd">{cmd}</span> <span className="comment"># {note}</span>
            </Line>
          ))}
        </WorkflowBox>

        <WorkflowBox id="quickstart" title="// QUICKSTART WORKFLOW">
          {QUICKSTART.map(([comment, cmd], i) => (
            <span key={comment}>
              {i > 0 && <span className="line gap" aria-hidden="true" />}
              <Line className="comment">{comment}</Line>
              <Line className="cmd">{cmd}</Line>
            </span>
          ))}
        </WorkflowBox>
      </main>

      <footer>
        <div className="container footer-inner">
          <div>
            xavierlabs-ai · MIT License · Created by{' '}
            <a href="https://adrianfolio.vercel.app/" target="_blank" rel="noopener noreferrer">Adrian Xavier Moral</a>
          </div>
          <div>
            <a href={REPO} target="_blank" rel="noopener noreferrer">GitHub Repository ↗</a>
          </div>
        </div>
      </footer>

      <AnimatePresence>
        {toast && (
          <motion.div
            className="toast"
            role="status"
            initial={{ opacity: 0, y: 24, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ type: 'spring', stiffness: 380, damping: 28 }}
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
