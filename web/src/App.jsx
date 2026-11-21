import { useEffect, useMemo, useState } from 'react';
import SplitText from './components/rb/SplitText.jsx';
import RotatingText from './components/rb/RotatingText.jsx';
import ShinyText from './components/rb/ShinyText.jsx';
import LogoLoop from './components/rb/LogoLoop.jsx';
import MagicBento from './components/rb/MagicBento.jsx';
import SpotlightCard from './components/rb/SpotlightCard.jsx';
import DotGrid from './components/rb/DotGrid.jsx';
import TerminalCard from './components/TerminalCard.jsx';
import {
  CheckIcon,
  CopyIcon,
  DocumentIcon,
  FlaskIcon,
  GitHubIcon,
  Mark,
  MoonIcon,
  SearchIcon,
  ShieldCheckIcon,
  SunIcon
} from './components/Icons.jsx';

const REPO_URL = 'https://github.com/venstqs/XavierLabs-AI';
const REPO_GIT = `${REPO_URL}.git`;
const THEME_KEY = 'xavierlabs-ai-theme';

const ROTATING_PHRASES = [
  'searches ArXiv & Semantic Scholar',
  'scores hypotheses before running code',
  'debugs failing sandbox runs automatically',
  'compiles LaTeX, PDF, HTML & plots'
];

const TAGS = [
  'ArXiv',
  'Semantic Scholar',
  'LiteLLM',
  'Groq',
  'DeepSeek',
  'OpenRouter',
  'Ollama',
  'Gemini',
  'Docker',
  'NumPy',
  'SciPy',
  'Matplotlib',
  'SQLite',
  'LaTeX'
];

const INSTALL_CMDS = {
  pip: `pip install git+${REPO_GIT}`,
  uv: `uv pip install git+${REPO_GIT}`,
  git: `git clone ${REPO_GIT} && cd XavierLabs-AI && pip install -e .`
};

const CLI_COMMANDS = [
  ['xavier', 'Launch interactive research console'],
  ['xavier research "question"', 'Run the full 4-agent loop to paper'],
  ['xavier paper <folder> --open', 'Open generated PDF / HTML paper'],
  ['xavier history', 'Browse past runs and metrics']
];

const BENTO_THEME_STYLES = {
  dark: {
    '--mb-surface': 'linear-gradient(180deg, #0b0b0b 0%, #050505 100%)',
    '--mb-edge': '#1a1a1a',
    '--mb-highlight': 'rgba(255, 255, 255, 0.04)',
    '--mb-shadow': '0 20px 40px -28px rgba(0, 0, 0, 0.9)',
    '--mb-tile': 'linear-gradient(180deg, #141414 0%, #0a0a0a 100%)',
    '--mb-tile-edge': '#222222',
    '--mb-ink': '#f5f5f5',
    '--mb-muted': '#8a8a8a',
    '--mb-faint': '#555555',
    '--mb-line': '#1a1a1a'
  },
  light: {
    '--mb-surface': 'linear-gradient(180deg, #ffffff 0%, #fafafa 100%)',
    '--mb-edge': '#e5e5e5',
    '--mb-highlight': '#ffffff',
    '--mb-shadow': '0 16px 32px -24px rgba(0, 0, 0, 0.12)',
    '--mb-tile': 'linear-gradient(180deg, #ffffff 0%, #f4f4f4 100%)',
    '--mb-tile-edge': '#e2e2e2',
    '--mb-ink': '#0a0a0a',
    '--mb-muted': '#5c5c5c',
    '--mb-faint': '#999999',
    '--mb-line': '#e5e5e5'
  }
};

function readInitialTheme() {
  if (typeof document === 'undefined') return 'dark';
  return document.documentElement.dataset.theme === 'light' ? 'light' : 'dark';
}

function copyText(text, onDone) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(onDone).catch(() => {});
  } else {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      onDone();
    } catch {
      /* ignore */
    }
    document.body.removeChild(ta);
  }
}

export default function App() {
  const [theme, setTheme] = useState(readInitialTheme);
  const [activeSection, setActiveSection] = useState('top');
  const [installTab, setInstallTab] = useState('pip');
  const [copiedHero, setCopiedHero] = useState(false);
  const [copiedInstall, setCopiedInstall] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch {
      /* ignore */
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#000000' : '#ffffff');
  }, [theme]);

  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') return undefined;
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) setActiveSection(entry.target.id);
        });
      },
      { rootMargin: '-40% 0px -50% 0px' }
    );

    ['top', 'pipeline', 'install'].forEach(id => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const toggleTheme = () => setTheme(t => (t === 'light' ? 'dark' : 'light'));

  const tagLogos = useMemo(
    () =>
      TAGS.map(label => ({
        node: <span className="tag">{label}</span>,
        ariaLabel: label
      })),
    []
  );

  const pipelineItems = useMemo(
    () => [
      {
        id: 'find',
        label: 'STAGE 01',
        icon: <SearchIcon />,
        title: 'Literature & Hypothesis',
        description:
          'Queries ArXiv and Semantic Scholar, synthesizes prior work, and formulates a falsifiable hypothesis with clear metrics.'
      },
      {
        id: 'review',
        label: 'STAGE 02',
        icon: <ShieldCheckIcon />,
        title: 'Adversarial Review',
        description:
          'A dedicated reviewer agent scores novelty and experimental rigor, rejecting weak plans before a single line of code runs.'
      },
      {
        id: 'experiment',
        label: 'STAGE 03',
        icon: <FlaskIcon size={17} />,
        title: 'Sandboxed Execution',
        description:
          'Writes and runs Python in an isolated sandbox. When a run crashes, it inspects the traceback and patches its own code.'
      },
      {
        id: 'write',
        label: 'STAGE 04',
        icon: <DocumentIcon />,
        title: 'Paper Synthesis',
        description:
          'Generates publication plots from real execution outputs and compiles the final report to PDF, LaTeX, HTML, and Markdown.'
      }
    ],
    []
  );

  return (
    <>
      <header className="topbar">
        <div className="wrap topbar-inner">
          <a className="brand" href="#top">
            <Mark id="nav-mark-m" />
            <span>XavierLabs AI</span>
            <span className="brand-tag">MIT</span>
          </a>

          <nav className="nav-links" aria-label="Main">
            <a href="#pipeline" className={activeSection === 'pipeline' ? 'active' : ''}>
              Pipeline
            </a>
            <a href="#install" className={activeSection === 'install' ? 'active' : ''}>
              Install
            </a>
            <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
              Docs
            </a>
          </nav>

          <div className="nav-actions">
            <button
              className="icon-btn"
              type="button"
              onClick={toggleTheme}
              aria-label="Toggle color theme"
            >
              {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
            </button>
            <a
              className="btn btn-solid btn-sm"
              href={REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
            >
              <GitHubIcon size={15} />
              GitHub
            </a>
          </div>
        </div>
      </header>

      <main>
        <section className="hero" id="top">
          <div className="hero-dots" aria-hidden="true">
            <DotGrid
              dotSize={2.8}
              gap={26}
              baseColor={theme === 'dark' ? '#1e1e1e' : '#dcdcdc'}
              activeColor={theme === 'dark' ? '#888888' : '#222222'}
              proximity={130}
              strength={0.5}
              opacity={theme === 'dark' ? 0.75 : 0.6}
              mouseInteraction
              clickShock={false}
            />
          </div>

          <div className="wrap">
            <div className="hero-head">
              <p className="eyebrow">
                <span className="dot" />
                <ShinyText
                  text="Terminal-Native Computational Research Swarm"
                  color={theme === 'dark' ? '#8a8a8a' : '#5c5c5c'}
                  shineColor={theme === 'dark' ? '#ffffff' : '#0a0a0a'}
                  speed={3.4}
                />
              </p>

              <SplitText
                text="From question to paper."
                tag="h1"
                className="hero-title"
                textAlign="center"
                splitType="chars"
                delay={24}
                duration={0.75}
                effect="rise"
              />

              <p className="hero-sub">
                Give XavierLabs AI a research question in your terminal. Four specialized agents
                run real experiments in a sandbox so every figure and number in the paper comes from
                code that actually executed.
              </p>

              <div className="hero-rotate-line">
                <span>$ xavier &rarr;</span>
                <RotatingText
                  texts={ROTATING_PHRASES}
                  mainClassName="rotate-inline"
                  rotationInterval={2600}
                  staggerDuration={0.015}
                  splitBy="words"
                  effect="slide"
                  direction="up"
                />
              </div>

              <div className="hero-actions">
                <div className="hero-cmd">
                  <span>{INSTALL_CMDS.pip}</span>
                  <button
                    className={`icon-btn${copiedHero ? ' copied' : ''}`}
                    type="button"
                    aria-label={copiedHero ? 'Copied' : 'Copy pip install command'}
                    onClick={() =>
                      copyText(INSTALL_CMDS.pip, () => {
                        setCopiedHero(true);
                        setTimeout(() => setCopiedHero(false), 1400);
                      })
                    }
                  >
                    {copiedHero ? <CheckIcon size={14} /> : <CopyIcon size={14} />}
                  </button>
                </div>
                <a className="btn btn-outline" href="#pipeline">
                  How it works
                </a>
              </div>
            </div>

            <div className="workbench-wrap">
              <TerminalCard theme={theme} />
            </div>
          </div>
        </section>

        <div className="ecosystem" aria-label="Works with">
          <LogoLoop
            logos={tagLogos}
            speed={46}
            gap={10}
            logoHeight={30}
            pauseOnHover
            fadeOut
            fadeOutWidth={0.1}
            draggable
            ariaLabel="Supported tools and model providers"
          />
        </div>

        <section className="wrap section" id="pipeline">
          <p className="section-kicker">Architecture</p>
          <h2>Four agents, one verified loop.</h2>
          <p className="section-sub">
            No fabricated citations or hallucinated benchmarks. Each stage hands structured
            artifacts to the next.
          </p>

          <MagicBento
            className="steps-bento"
            items={pipelineItems}
            columns={2}
            rowHeight={185}
            gap={14}
            radius={14}
            theme={theme}
            glowColor={theme === 'dark' ? '#ffffff' : '#0a0a0a'}
            textAutoHide={false}
            enableSpotlight
            enableBorderGlow
            enableTilt={false}
            clickEffect
            style={BENTO_THEME_STYLES[theme]}
          />
        </section>

        <section className="wrap section" id="install">
          <p className="section-kicker">Quickstart</p>
          <h2>Run it locally in a minute.</h2>
          <p className="section-sub">
            Requires Python 3.10+. Bring any cloud model via LiteLLM, or run completely offline with
            Ollama.
          </p>

          <div className="install-grid">
            <div className="install-panel">
              <div className="seg" role="tablist" aria-label="Install method">
                {Object.keys(INSTALL_CMDS).map(tab => (
                  <button
                    key={tab}
                    type="button"
                    role="tab"
                    aria-selected={installTab === tab}
                    className={`seg-btn${installTab === tab ? ' active' : ''}`}
                    onClick={() => {
                      setInstallTab(tab);
                      setCopiedInstall(false);
                    }}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <SpotlightCard
                className="code-card"
                theme={theme}
                intensity={theme === 'dark' ? 0.1 : 0.06}
                borderGlow={0.4}
                spotlightSize={220}
              >
                <div className="code-row">
                  <code>{INSTALL_CMDS[installTab]}</code>
                  <button
                    className={`icon-btn${copiedInstall ? ' copied' : ''}`}
                    type="button"
                    aria-label={copiedInstall ? 'Copied' : 'Copy install command'}
                    onClick={() =>
                      copyText(INSTALL_CMDS[installTab], () => {
                        setCopiedInstall(true);
                        setTimeout(() => setCopiedInstall(false), 1400);
                      })
                    }
                  >
                    {copiedInstall ? <CheckIcon size={15} /> : <CopyIcon size={15} />}
                  </button>
                </div>
              </SpotlightCard>

              <p className="install-note">
                Configure your provider key in <code>.env</code> or point <code>OLLAMA_BASE_URL</code>{' '}
                to a local model, then launch <code>xavier</code>.
              </p>
            </div>

            <div className="cmd-panel">
              <div className="cmd-panel-head">CLI Commands</div>
              <div className="cmd-list">
                {CLI_COMMANDS.map(([cmd, desc]) => (
                  <div key={cmd}>
                    <code>{cmd}</code>
                    <span>{desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <footer className="wrap footer">
          <a className="footer-brand" href="#top">
            <Mark id="footer-mark-m" />
            XavierLabs AI
          </a>
          <span>Built by Adrian Xavier Moral</span>
          <div className="footer-links">
            <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            <span>MIT License</span>
          </div>
        </footer>
      </main>
    </>
  );
}
