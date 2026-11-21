import { useEffect, useMemo, useState } from 'react';
import Threads from './components/rb/Threads.jsx';
import SplitText from './components/rb/SplitText.jsx';
import RotatingText from './components/rb/RotatingText.jsx';
import ShinyText from './components/rb/ShinyText.jsx';
import LogoLoop from './components/rb/LogoLoop.jsx';
import MagicBento from './components/rb/MagicBento.jsx';
import SpotlightCard from './components/rb/SpotlightCard.jsx';
import DotGrid from './components/rb/DotGrid.jsx';
import Dock from './components/rb/Dock.jsx';
import TerminalCard from './components/TerminalCard.jsx';
import {
  CheckIcon,
  CopyIcon,
  DocumentIcon,
  FlaskIcon,
  GitHubIcon,
  HomeIcon,
  Mark,
  MoonIcon,
  SearchIcon,
  ShieldCheckIcon,
  SunIcon,
  TerminalIcon
} from './components/Icons.jsx';

const REPO_URL = 'https://github.com/venstqs/XavierLabs-AI';
const REPO_GIT = `${REPO_URL}.git`;

const ROTATING_WORDS = [
  'reads the literature',
  'tests a hypothesis',
  'runs real experiments',
  'fixes its own bugs',
  'writes the paper'
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
  ['xavier', 'Open the interactive console'],
  ['xavier research "your question"', 'Run the full loop and get a paper'],
  ['xavier paper <folder> --open', 'Open a finished paper'],
  ['xavier history', 'See past runs']
];

const BENTO_THEME_STYLES = {
  dark: {
    '--mb-surface': 'linear-gradient(180deg, #141414 0%, #0e0e0e 100%)',
    '--mb-edge': '#232323',
    '--mb-highlight': 'rgba(255, 255, 255, 0.05)',
    '--mb-shadow': '0 24px 48px -28px rgba(0, 0, 0, 0.85)',
    '--mb-tile': 'linear-gradient(180deg, #1f1f1f 0%, #141414 100%)',
    '--mb-tile-edge': '#2c2c2c',
    '--mb-ink': '#f5f5f5',
    '--mb-muted': '#a3a3a3',
    '--mb-faint': '#6b6b6b',
    '--mb-line': '#232323'
  },
  light: {
    '--mb-surface': 'linear-gradient(180deg, #ffffff 0%, #fafafa 100%)',
    '--mb-edge': '#e7e7e7',
    '--mb-highlight': '#ffffff',
    '--mb-shadow': '0 18px 36px -26px rgba(0, 0, 0, 0.14)',
    '--mb-tile': 'linear-gradient(180deg, #ffffff 0%, #f4f4f4 100%)',
    '--mb-tile-edge': '#e2e2e2',
    '--mb-ink': '#0a0a0a',
    '--mb-muted': '#616161',
    '--mb-faint': '#9a9a9a',
    '--mb-line': '#e7e7e7'
  }
};

const DOCK_THEME_STYLES = {
  dark: {
    '--dock-panel': 'rgba(17, 17, 17, 0.86)',
    '--dock-panel-edge': '#262626',
    '--dock-panel-highlight': 'rgba(255, 255, 255, 0.06)',
    '--dock-tile': 'linear-gradient(180deg, #1b1b1b 0%, #0f0f0f 100%)',
    '--dock-tile-edge': '#2a2a2a',
    '--dock-tile-highlight': 'rgba(255, 255, 255, 0.08)',
    '--dock-ink': '#f5f5f5',
    '--dock-label-bg': '#141414',
    '--dock-label-edge': '#2a2a2a'
  },
  light: {
    '--dock-panel': 'rgba(255, 255, 255, 0.86)',
    '--dock-panel-edge': '#e5e5e5',
    '--dock-panel-highlight': '#ffffff',
    '--dock-tile': 'linear-gradient(180deg, #ffffff 0%, #f5f5f5 100%)',
    '--dock-tile-edge': '#e5e5e5',
    '--dock-tile-highlight': '#ffffff',
    '--dock-ink': '#0a0a0a',
    '--dock-label-bg': '#ffffff',
    '--dock-label-edge': '#e5e5e5'
  }
};

function readInitialTheme() {
  if (typeof document === 'undefined') return 'dark';
  return document.documentElement.dataset.theme === 'light' ? 'light' : 'dark';
}

export default function App() {
  const [theme, setTheme] = useState(readInitialTheme);
  const [activeSection, setActiveSection] = useState('about');
  const [installTab, setInstallTab] = useState('pip');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem('theme', theme);
    } catch {
      /* ignore */
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#0a0a0a' : '#ffffff');
  }, [theme]);

  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') return undefined;
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) setActiveSection(entry.target.id);
        });
      },
      { rootMargin: '-45% 0px -50% 0px' }
    );

    ['about', 'how', 'install'].forEach(id => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const toggleTheme = () => setTheme(t => (t === 'light' ? 'dark' : 'light'));

  const handleCopy = () => {
    const text = INSTALL_CMDS[installTab];
    const markCopied = () => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(markCopied).catch(() => {});
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
        markCopied();
      } catch {
        /* ignore */
      }
      document.body.removeChild(ta);
    }
  };

  const scrollToSection = id => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const tagLogos = useMemo(
    () =>
      TAGS.map(label => ({
        node: <span className="tag">{label}</span>,
        ariaLabel: label
      })),
    []
  );

  const stepsItems = useMemo(
    () => [
      {
        id: 'find',
        label: '01',
        icon: <SearchIcon />,
        title: 'Find',
        description: 'Searches ArXiv and Semantic Scholar, then writes a hypothesis you can test.'
      },
      {
        id: 'review',
        label: '02',
        icon: <ShieldCheckIcon />,
        title: 'Review',
        description: 'A reviewer agent scores the idea and sends weak ones back before any code runs.'
      },
      {
        id: 'experiment',
        label: '03',
        icon: <FlaskIcon size={17} />,
        title: 'Experiment',
        description: 'Writes Python and runs it in a sandbox. If it crashes, it reads the error and fixes it.'
      },
      {
        id: 'write',
        label: '04',
        icon: <DocumentIcon />,
        title: 'Write',
        description: 'Plots the results and writes the paper as PDF, LaTeX, HTML and Markdown.'
      }
    ],
    []
  );

  const dockItems = useMemo(
    () => [
      {
        label: 'Top',
        icon: <HomeIcon />,
        active: activeSection === 'about',
        onClick: () => scrollToSection('top')
      },
      {
        label: 'How it works',
        icon: <FlaskIcon />,
        active: activeSection === 'how',
        onClick: () => scrollToSection('how')
      },
      {
        label: 'Install',
        icon: <TerminalIcon />,
        active: activeSection === 'install',
        onClick: () => scrollToSection('install')
      },
      { separator: true },
      {
        label: 'GitHub',
        icon: <GitHubIcon size={18} />,
        onClick: () => window.open(REPO_URL, '_blank', 'noopener,noreferrer')
      },
      {
        label: theme === 'dark' ? 'Light mode' : 'Dark mode',
        icon: theme === 'dark' ? <SunIcon size={18} /> : <MoonIcon size={18} />,
        onClick: toggleTheme
      }
    ],
    [activeSection, theme]
  );

  const threadsColor = theme === 'dark' ? [0.96, 0.96, 0.96] : [0.06, 0.06, 0.06];

  return (
    <>
      <div className="navwrap">
        <nav className="wrap nav" aria-label="Main">
          <a className="logo" href="#top">
            <Mark id="nav-mark-m" />
            <span>XavierLabs</span>
          </a>
          <div className="pill-nav">
            <a href="#about" className={activeSection === 'about' ? 'active' : ''}>
              About
            </a>
            <a href="#how" className={activeSection === 'how' ? 'active' : ''}>
              How it works
            </a>
            <a href="#install" className={activeSection === 'install' ? 'active' : ''}>
              Install
            </a>
          </div>
          <div className="nav-right">
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
              <GitHubIcon />
              GitHub
            </a>
          </div>
        </nav>
      </div>

      <main id="top">
        <section className="hero" id="about">
          <div className="hero-bg" aria-hidden="true">
            <Threads
              color={threadsColor}
              amplitude={1.3}
              distance={0.32}
              lineCount={64}
              speed={0.45}
              thickness={0.55}
              angle={18}
              enableMouseInteraction={false}
            />
          </div>

          <div className="wrap hero-grid">
            <div className="hero-copy">
              <p className="status">
                <span className="dot" />
                <ShinyText
                  text="Open source research agent"
                  color={theme === 'dark' ? '#a3a3a3' : '#616161'}
                  shineColor={theme === 'dark' ? '#ffffff' : '#0a0a0a'}
                  speed={3.2}
                />
              </p>

              <SplitText
                text="Research on autopilot."
                tag="h1"
                className="hero-title"
                textAlign="left"
                splitType="chars"
                delay={28}
                duration={0.8}
                effect="rise"
              />

              <p className="rotator">
                <span>It</span>
                <RotatingText
                  texts={ROTATING_WORDS}
                  mainClassName="word-pill"
                  rotationInterval={2400}
                  staggerDuration={0.02}
                  splitBy="words"
                  effect="slide"
                  direction="up"
                />
              </p>

              <p className="intro">
                Give XavierLabs a question. A team of four AI agents finds the papers, tests a
                hypothesis with real code in a sandbox, fixes its own crashes, and hands you a
                finished paper.
              </p>

              <div className="cta">
                <a className="btn btn-solid" href="#install">
                  Get started
                </a>
                <a
                  className="btn btn-ghost"
                  href={REPO_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on GitHub
                </a>
              </div>
            </div>

            <TerminalCard theme={theme} />
          </div>

          <div className="tags" aria-label="Works with">
            <LogoLoop
              logos={tagLogos}
              speed={52}
              gap={12}
              logoHeight={34}
              pauseOnHover
              fadeOut
              fadeOutWidth={0.12}
              draggable
              ariaLabel="Supported tools and model providers"
            />
          </div>
        </section>

        <section className="wrap section" id="how">
          <h2>How it works</h2>
          <p className="section-sub">
            One command runs the whole loop. Every number in the paper comes from code that
            actually ran.
          </p>

          <MagicBento
            className="steps-bento"
            items={stepsItems}
            columns={4}
            rowHeight={215}
            gap={12}
            radius={20}
            theme={theme}
            glowColor={theme === 'dark' ? '#ffffff' : '#0a0a0a'}
            textAutoHide={false}
            enableSpotlight
            enableBorderGlow
            enableTilt
            clickEffect
            style={BENTO_THEME_STYLES[theme]}
          />
        </section>

        <section className="wrap section install-section" id="install">
          <h2>Install</h2>
          <p className="section-sub">
            Python 3.10 or newer. Works with any model provider, or offline with Ollama.
          </p>

          <div className="install-surface">
            <div className="install-dots" aria-hidden="true">
              <DotGrid
                dotSize={3.5}
                gap={22}
                baseColor={theme === 'dark' ? '#2c2c2c' : '#d4d4d4'}
                activeColor={theme === 'dark' ? '#ffffff' : '#0a0a0a'}
                proximity={120}
                strength={0.65}
                opacity={theme === 'dark' ? 0.55 : 0.45}
                mouseInteraction
                clickShock={false}
              />
            </div>

            <div className="install-inner">
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
                      setCopied(false);
                    }}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <SpotlightCard
                className="code-card"
                theme={theme}
                intensity={theme === 'dark' ? 0.12 : 0.08}
                borderGlow={0.5}
                spotlightSize={220}
              >
                <div className="code-row">
                  <code>{INSTALL_CMDS[installTab]}</code>
                  <button
                    className={`icon-btn${copied ? ' copied' : ''}`}
                    type="button"
                    onClick={handleCopy}
                    aria-label={copied ? 'Copied' : 'Copy install command'}
                  >
                    {copied ? <CheckIcon /> : <CopyIcon />}
                  </button>
                </div>
              </SpotlightCard>

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
          <a
            className="footer-brand"
            href="https://adrianfolio.vercel.app/"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Mark id="footer-mark-m" />
            XavierLabs
          </a>
          <span>Built by Adrian Xavier Moral</span>
          <span className="footer-right">MIT License</span>
        </footer>
      </main>

      <Dock
        className="floating-dock"
        items={dockItems}
        position="bottom"
        theme={theme}
        baseItemSize={42}
        magnification={58}
        distance={140}
        panelHeight={56}
        gap={6}
        roundness={0.55}
        accentColor={theme === 'dark' ? '#f5f5f5' : '#0a0a0a'}
        style={DOCK_THEME_STYLES[theme]}
      />
    </>
  );
}
