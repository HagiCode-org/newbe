import React, { useId } from 'react';
import styles from './styles.module.css';
import { HagicodeConfig, HAGICODE_CONFIG } from '../HagicodeConfig';

export type HagicodeRecommendationLayout = 'page' | 'modal';

interface HagicodeRecommendationProps {
  config?: HagicodeConfig;
  layout?: HagicodeRecommendationLayout;
}

const SMART_WORKFLOW_STEPS = ['Idea', 'Proposal', 'Tasks', 'Archive'];

const EFFICIENT_AGENT_LANES = [
  {
    name: 'Claude Code',
    tasks: ['Spec 起草', '设计校对', '归档检查'],
  },
  {
    name: 'Codex',
    tasks: ['实现 A', '实现 B', '回归修复'],
  },
  {
    name: 'Qwen · GLM',
    tasks: ['问题排查', '文案优化', '知识提炼'],
  },
];

const HERO_GALLERY_FILES = [
  'cat-line-03.webp',
  'cat-ink-09.webp',
  'cat-sticker-02.webp',
  'cat-sticker-08.webp',
  'thorn-06.webp',
  'cat-paper-04.webp',
  'tide-09.webp',
  'royal-10.webp',
  'cat-oil-09.webp',
  'aurora-04.webp',
];

const HERO_GALLERY_ASSETS = HERO_GALLERY_FILES.map((file) => ({
  src: `/img/hagicode-heroes/${file}`,
  alt: file
    .replace(/\.webp$/, '')
    .split('-')
    .map((p) => (p ? p[0].toUpperCase() + p.slice(1) : p))
    .join(' '),
}));

const HERO_GALLERY_LOOP = [...HERO_GALLERY_ASSETS, ...HERO_GALLERY_ASSETS];

const INTERESTING_METRICS = [
  { value: '4', label: '副本推进' },
  { value: 'Lv.27', label: '队长等级' },
  { value: '12.8M', label: '今日 XP' },
];

function FeatureVisual({ id }: { id: string }) {
  if (id === 'smart') {
    return (
      <div className={`${styles.featureVisual} ${styles.smartVisual}`} aria-hidden="true">
        <div className={styles.workflowVisual}>
          {SMART_WORKFLOW_STEPS.map((step) => (
            <span key={step} className={styles.workflowStep}>
              {step}
            </span>
          ))}
        </div>
        <div className={styles.workflowLine}>
          <span className={styles.workflowProgress} />
        </div>
      </div>
    );
  }

  if (id === 'efficient') {
    return (
      <div className={`${styles.featureVisual} ${styles.efficientVisual}`} aria-hidden="true">
        {EFFICIENT_AGENT_LANES.map((lane) => (
          <div key={lane.name} className={styles.agentLane}>
            <span className={styles.agentLaneName}>{lane.name}</span>
            <div className={styles.agentLaneTasks}>
              {lane.tasks.map((task) => (
                <span key={task} className={styles.agentTaskPill}>
                  {task}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`${styles.featureVisual} ${styles.interestingVisual}`} aria-hidden="true">
      <div className={styles.galleryViewport}>
        <div className={styles.galleryTrack}>
          {HERO_GALLERY_LOOP.map((asset, index) => (
            <div key={`${asset.src}-${index}`} className={styles.galleryCard}>
              <img
                src={asset.src}
                alt={asset.alt}
                className={styles.galleryImage}
                loading="lazy"
                decoding="async"
              />
            </div>
          ))}
        </div>
      </div>

      <div className={styles.metricRow}>
        {INTERESTING_METRICS.map((metric) => (
          <span key={metric.label} className={styles.metricCard}>
            <strong>{metric.value}</strong>
            <small>{metric.label}</small>
          </span>
        ))}
      </div>
    </div>
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
      <div className={styles.eyebrow}>★ Hagicode 推荐</div>
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
        <div>
          <p className={styles.showcaseTitle}>{config.showcase.title}</p>
          <p className={styles.showcaseSubtitle}>{config.showcase.subtitle}</p>
        </div>
      </div>

      <div className={styles.featureGrid} aria-label={config.showcase.title}>
        {config.showcase.items.map((item) => (
          <article
            key={item.id}
            className={`${styles.featureCard} ${styles[`tone${item.id[0].toUpperCase()}${item.id.slice(1)}`]}`}
          >
            <div className={styles.featureCardTop}>
              <span className={styles.featureBadge}>{item.badge}</span>
              <div className={styles.featureStat}>
                <span className={styles.featureStatValue}>{item.statValue}</span>
                <span className={styles.featureStatLabel}>{item.statLabel}</span>
              </div>
            </div>

            <div className={styles.featureCardBody}>
              <h4 className={styles.featureTitle}>{item.title}</h4>
              <p className={styles.featureSubtitle}>{item.subtitle}</p>
              <p className={styles.featureDescription}>{item.description}</p>
            </div>

            <FeatureVisual id={item.id} />

            <ul className={styles.featureHighlights} aria-label={`${item.title}重点`}>
              {item.highlights.map((highlight) => (
                <li key={highlight} className={styles.featureHighlight}>
                  {highlight}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
