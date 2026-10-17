import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import styles from './styles.module.css';
import { HagicodeConfig, HagicodeShowcaseItem, HAGICODE_CONFIG } from '../HagicodeConfig';

export type HagicodeRecommendationLayout = 'page' | 'modal';

/**
 * static  – server render / reduced motion / no IntersectionObserver: every stage shows its finished state.
 * pre     – mounted, card not yet seen: stage sits in its starting state (nobody can see it).
 * play    – card entered the viewport: the stage plays its effect once.
 * done    – effect finished; the stage rests in its finished state until the replay button is used.
 */
type Phase = 'static' | 'pre' | 'play' | 'done';

type CssVars = React.CSSProperties & Record<`--${string}`, string | number>;
const vars = (v: CssVars): React.CSSProperties => v;

const SMART_WORKFLOW_STEPS = ['Idea', 'Proposal', 'Tasks', 'Archive'];

type CliKind = 'tool' | 'ok';

interface CliPane {
  agent: string;
  /** The CLI command the session was started with, shown on the pane's title row. */
  command: string;
  lines: Array<{ kind: CliKind; text: string }>;
}

/** Illustrative sessions: each CLI works on its own slice of the same change, side by side. */
const CLI_PANES: CliPane[] = [
  {
    agent: 'Claude Code',
    command: 'claude',
    lines: [
      { kind: 'tool', text: 'Write  design.md' },
      { kind: 'ok', text: 'spec 校验通过' },
    ],
  },
  {
    agent: 'Codex',
    command: 'codex',
    lines: [
      { kind: 'tool', text: 'Edit  src/auth.ts' },
      { kind: 'ok', text: '回归测试通过' },
    ],
  },
  {
    agent: 'Qwen · GLM',
    command: 'qwen',
    lines: [
      { kind: 'tool', text: 'Grep  refresh token' },
      { kind: 'ok', text: '定位到超时原因' },
    ],
  },
];

/** Seconds between pane starts, typing speed (seconds per character) and the pause before a line. */
const PANE_STAGGER = 0.3;
const TYPE_RATE = 0.045;
const LINE_GAP = 0.25;

const HERO_FILES = [
  'cat-line-03.webp',
  'aurora-04.webp',
  'cat-sticker-02.webp',
  'thorn-06.webp',
  'royal-10.webp',
  'tide-09.webp',
  'cat-oil-09.webp',
  'cat-paper-04.webp',
];

const heroSrc = (file: string) => `/img/hagicode-heroes/${file}`;

/** Illustrative demo values for the Hero Dungeon report, matched to the highlights by position. */
const REPORT_VALUES: Array<{ value?: string; unit?: string; team?: boolean }> = [
  { value: '4', unit: '副本推进' },
  { team: true },
  { value: '12.8M', unit: '今日 XP' },
];

interface StageMeta {
  label: string;
  path: string;
  status: string;
  /** Seconds after the card's own start when the status chip appears. */
  statusAt: number;
  /** Rough length of the whole effect, used only to flip phase play -> done. */
  playMs: number;
  /** Replay on its own while the card is on screen. */
  loop?: boolean;
}

/** Pause between the end of one automatic run and the next. */
const LOOP_HOLD_MS = 2600;

const STAGE_META: Record<string, StageMeta> = {
  smart: { label: 'SMART', path: 'openspec / proposal', status: '已归档', statusAt: 3.1, playMs: 4200, loop: true },
  efficient: { label: 'EFFICIENT', path: 'cli / parallel', status: '并行完成', statusAt: 3.5, playMs: 5000 },
  interesting: { label: 'INTERESTING', path: 'hero dungeon / 战报', status: '战报生成', statusAt: 1.5, playMs: 3200 },
};

const FALLBACK_META: StageMeta = STAGE_META.smart;

/** Splits a numeric stat such as "300%", "10x+" or "Lv.27" into prefix / number / suffix for the count-up. */
function splitStat(value: string) {
  const match = value.match(/^(\D*)(\d+)(.*)$/);
  if (!match) return null;
  return { prefix: match[1], num: Number(match[2]), suffix: match[3] };
}

function useShowcasePhase(playMs: number, loop: boolean) {
  const ref = useRef<HTMLElement | null>(null);
  const [phase, setPhase] = useState<Phase>('static');
  const [run, setRun] = useState(0);
  const [visible, setVisible] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [tabVisible, setTabVisible] = useState(true);

  useEffect(() => {
    const el = ref.current;
    if (
      !el ||
      typeof IntersectionObserver === 'undefined' ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      return undefined;
    }
    setPhase('pre');
    const observer = new IntersectionObserver(
      (entries) => {
        const on = entries.some((entry) => entry.isIntersecting);
        setVisible(on);
        if (!on) return;
        setPhase((current) => (current === 'pre' ? 'play' : current));
        // Looping cards keep watching so they can pause off screen.
        if (!loop) observer.disconnect();
      },
      { threshold: 0.3 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [loop]);

  useEffect(() => {
    if (!loop) return undefined;
    const onChange = () => setTabVisible(!document.hidden);
    document.addEventListener('visibilitychange', onChange);
    return () => document.removeEventListener('visibilitychange', onChange);
  }, [loop]);

  useEffect(() => {
    if (phase !== 'play') return undefined;
    // Cards stagger by up to ~0.6s in the three-column layout; leave room for that.
    const timer = window.setTimeout(() => setPhase('done'), playMs + 900);
    return () => window.clearTimeout(timer);
  }, [phase, run, playMs]);

  const replay = useCallback(() => {
    setRun((value) => value + 1);
    setPhase('play');
  }, []);

  // Auto-play: run again after a pause, but only while the card is seen, not hovered, and the tab is in front.
  useEffect(() => {
    if (!loop || phase !== 'done' || !visible || hovered || !tabVisible) return undefined;
    const timer = window.setTimeout(replay, LOOP_HOLD_MS);
    return () => window.clearTimeout(timer);
  }, [loop, phase, visible, hovered, tabVisible, replay]);

  return { ref, phase, run, replay, setHovered };
}

function Arrow() {
  return (
    <svg className={styles.arrow} viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M3 8h9.5M9 4.5 12.5 8 9 11.5" />
    </svg>
  );
}

function SmartStage({ item }: { item: HagicodeShowcaseItem }) {
  return (
    <>
      <div className={styles.rail}>
        <span className={styles.railLine}>
          <span className={styles.railFill} />
        </span>
        {SMART_WORKFLOW_STEPS.map((step, index) => (
          <span key={step} className={styles.railNode} style={vars({ '--i': index })}>
            <span className={styles.railDot} />
            <span className={styles.railLabel}>{step}</span>
          </span>
        ))}
      </div>
      <ul className={styles.specRows}>
        {item.highlights.map((highlight, index) => {
          const parts = highlight.split('->').map((part) => part.trim());
          return (
            <li key={highlight} className={styles.specRow} style={vars({ '--i': index })}>
              <span className={styles.check}>
                <svg viewBox="0 0 16 16" fill="none">
                  <path d="M3.5 8.5 6.5 11.5 12.5 4.5" pathLength={1} />
                </svg>
              </span>
              {parts.map((part, partIndex) => (
                <React.Fragment key={part}>
                  {partIndex > 0 && <Arrow />}
                  <span>{part}</span>
                </React.Fragment>
              ))}
            </li>
          );
        })}
      </ul>
    </>
  );
}

function EfficientStage() {
  const typed = (text: string, start: number) => {
    const duration = text.length * TYPE_RATE;
    return { duration, style: vars({ '--ls': `${start.toFixed(2)}s`, '--tdur': `${duration.toFixed(2)}s`, '--n': text.length }) };
  };

  return (
    <>
      <div className={styles.cliPanes}>
        {CLI_PANES.map((pane, paneIndex) => {
          const paneStart = paneIndex * PANE_STAGGER;
          let cursor = paneStart + 0.2;
          const rows = pane.lines.map((line) => {
            const t = typed(line.text, cursor);
            cursor += t.duration + LINE_GAP;
            return { ...line, style: t.style };
          });
          return (
            <div
              key={pane.agent}
              className={styles.cliPane}
              style={vars({ '--ps': `${paneStart.toFixed(2)}s`, '--pe': `${(cursor - LINE_GAP).toFixed(2)}s` })}
            >
              <div className={styles.cliBar}>
                <span className={styles.cliState}>
                  <span className={styles.cliSpinner} />
                  <span className={styles.cliDone} />
                </span>
                <b>{pane.agent}</b>
                <span className={styles.cliCmd}>$ {pane.command}</span>
              </div>
              <ol className={styles.cliLines}>
                {rows.map((row) => (
                  <li
                    key={row.text}
                    className={`${styles.cliLine} ${row.kind === 'ok' ? styles.cliOk : styles.cliTool}`}
                    style={row.style}
                  >
                    <span className={styles.cliText}>{row.text}</span>
                  </li>
                ))}
              </ol>
            </div>
          );
        })}
      </div>
      <p className={styles.cliFoot} style={vars({ '--ls': '3s', '--tdur': '0.9s', '--n': 9 })}>
        <span className={styles.cliFootText}>结果汇入同一个提案</span>
      </p>
    </>
  );
}

function InterestingStage({ item }: { item: HagicodeShowcaseItem }) {
  const fan = HERO_FILES.slice(0, 5);
  const team = HERO_FILES.slice(5, 8);

  return (
    <>
      <div className={styles.fan}>
        {fan.map((file, index) => {
          const offset = index - 2;
          const distance = Math.abs(offset);
          return (
            <span
              key={file}
              className={styles.fanCard}
              style={vars({
                '--x': `${offset * 1.8}rem`,
                '--y': `${distance * distance * 0.16 + distance * 0.1}rem`,
                '--r': `${offset * 8}deg`,
                '--k': distance,
                zIndex: 10 - distance,
              })}
            >
              <img src={heroSrc(file)} alt="" width={96} height={96} loading="lazy" decoding="async" />
            </span>
          );
        })}
      </div>
      <ul className={styles.report}>
        {item.highlights.map((highlight, index) => {
          const entry = REPORT_VALUES[index];
          return (
            <li key={highlight} className={styles.reportRow} style={vars({ '--i': index })}>
              <span>{highlight}</span>
              {entry?.team ? (
                <span className={styles.team}>
                  {team.map((file) => (
                    <img key={file} src={heroSrc(file)} alt="" width={40} height={40} loading="lazy" decoding="async" />
                  ))}
                </span>
              ) : entry ? (
                <span className={styles.reportValue}>
                  <strong>{entry.value}</strong> {entry.unit}
                </span>
              ) : null}
            </li>
          );
        })}
      </ul>
    </>
  );
}

function ReplayIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M13 8a5 5 0 1 1-1.6-3.7" />
      <path d="M13 2.5v3h-3" />
    </svg>
  );
}

function ShowcaseCard({ item, index }: { item: HagicodeShowcaseItem; index: number }) {
  const meta = STAGE_META[item.id] ?? FALLBACK_META;
  const { ref, phase, run, replay, setHovered } = useShowcasePhase(meta.playMs, Boolean(meta.loop));
  const frame = useRef(0);
  const stat = splitStat(item.statValue);

  useEffect(() => () => cancelAnimationFrame(frame.current), []);

  // Cursor-follow light on the card body; fine pointers only, written straight to CSS variables.
  const onPointerMove = (event: React.PointerEvent<HTMLElement>) => {
    if (event.pointerType === 'touch') return;
    const el = event.currentTarget;
    const { clientX, clientY } = event;
    cancelAnimationFrame(frame.current);
    frame.current = requestAnimationFrame(() => {
      const box = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${clientX - box.left}px`);
      el.style.setProperty('--my', `${clientY - box.top}px`);
    });
  };

  return (
    <article
      ref={ref}
      className={styles.featureCard}
      data-tone={item.id}
      data-phase={phase}
      style={vars({ '--idx': index, '--status-at': `${meta.statusAt}s` })}
      onPointerMove={onPointerMove}
      onPointerEnter={(event) => event.pointerType === 'mouse' && setHovered(true)}
      onPointerLeave={() => setHovered(false)}
    >
      <div className={styles.stage}>
        <div className={styles.stageChrome}>
          <span className={styles.stageLabel} aria-hidden="true">
            <b>{meta.label}</b>
            <span>{meta.path}</span>
          </span>
          <span className={styles.stageStatus} aria-hidden="true">
            {meta.status}
          </span>
          <button type="button" className={styles.replay} onClick={replay} aria-label={`重新播放「${item.title}」演示`}>
            <ReplayIcon />
          </button>
        </div>
        <div key={run} className={`${styles.stageBody} ${run > 0 ? styles.stageFresh : ''}`} aria-hidden="true">
          {item.id === 'efficient' ? (
            <EfficientStage />
          ) : item.id === 'interesting' ? (
            <InterestingStage item={item} />
          ) : (
            <SmartStage item={item} />
          )}
        </div>
      </div>

      <div className={styles.cardBody}>
        <h4 className={styles.featureTitle}>{item.title}</h4>
        <p className={styles.featureSubtitle}>{item.subtitle}</p>
        <p className={styles.featureDescription}>{item.description}</p>
        <ul className={styles.srOnly} aria-label={`${item.title}重点`}>
          {item.highlights.map((highlight) => (
            <li key={highlight}>{highlight}</li>
          ))}
        </ul>

        <div className={styles.outcome}>
          <span className={styles.outcomeLabel}>{item.statLabel}</span>
          <span className={styles.srOnly}>{item.statValue}</span>
          <span className={styles.outcomeValue} aria-hidden="true">
            {stat ? (
              <>
                {stat.prefix}
                <span className={styles.count} style={vars({ '--to': stat.num })} />
                {stat.suffix}
              </>
            ) : (
              item.statValue
            )}
          </span>
        </div>
      </div>
    </article>
  );
}

export default function HagicodeRecommendation({
  config = HAGICODE_CONFIG,
  layout = 'page',
}: HagicodeRecommendationProps) {
  const titleId = useId();

  return (
    <section
      className={`${styles.promo} ${layout === 'modal' ? styles.modal : styles.page}`}
      aria-labelledby={titleId}
    >
      <div className={styles.inner}>
        <div className={styles.copy}>
          <h3 id={titleId} className={styles.title}>
            {config.name}
          </h3>
          <p className={styles.tagline}>{config.tagline}</p>
          <p className={styles.description}>{config.description}</p>
        </div>

        <div className={styles.actions}>
          <a
            href={config.links.installation}
            target="_blank"
            rel="noopener noreferrer"
            className={`${styles.ctaButton} ${styles.ctaPrimary}`}
            aria-label={`${config.modal.ctaButtons.install}（新标签页打开）`}
          >
            {config.modal.ctaButtons.install}
          </a>
          <a
            href={config.links.video}
            target="_blank"
            rel="noopener noreferrer"
            className={`${styles.ctaButton} ${styles.ctaSecondary}`}
            aria-label={`${config.modal.ctaButtons.video}（新标签页打开）`}
          >
            {config.modal.ctaButtons.video}
          </a>
        </div>
      </div>

      <div className={styles.showcaseHeader}>
        <p className={styles.showcaseTitle}>{config.showcase.title}</p>
        <p className={styles.showcaseSubtitle}>{config.showcase.subtitle}</p>
      </div>

      <div className={styles.featureGrid} role="group" aria-label={config.showcase.title}>
        {config.showcase.items.map((item, index) => (
          <ShowcaseCard key={item.id} item={item} index={index} />
        ))}
      </div>
    </section>
  );
}

interface HagicodeRecommendationProps {
  config?: HagicodeConfig;
  layout?: HagicodeRecommendationLayout;
}
