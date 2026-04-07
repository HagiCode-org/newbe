import React from 'react';
import styles from './index.module.css';
import { HagicodeConfig, HAGICODE_CONFIG } from '../HagicodeConfig';

interface HagicodeAdProps {
  config?: HagicodeConfig;
  compact?: boolean;
}

/**
 * HagicodeAd Component
 *
 * Displays an in-article promotional banner for Hagicode product.
 * Designed to be shown at the bottom of Mic blog articles.
 *
 * Features:
 * - Card-style design with visual separation from article content
 * - Responsive layout for mobile and desktop
 * - Two CTA buttons: installation and documentation
 * - Optional compact mode for tighter spacing
 */
export default function HagicodeAd({ config = HAGICODE_CONFIG, compact = false }: HagicodeAdProps) {
  const containerClass = compact ? `${styles.adContainer} ${styles.adCompact}` : styles.adContainer;
  const compactFeatures = config.features.items
    .slice(0, 4)
    .map((feature) => feature.split(' - ')[0])
    .join('  •  ');

  return (
    <>
      <hr className={styles.separator} />
      <div className={containerClass}>
        {/* Header */}
        <div className={styles.header}>
          <span className={styles.headerIcon}>🎯</span>
          <h3 className={styles.headerTitle}>推荐工具：{config.name}</h3>
        </div>

        {/* Content */}
        <div className={styles.content}>
          <h4 className={styles.productName}>
            {config.name} - {config.tagline}
          </h4>
          <p className={styles.features}>
            {compact ? compactFeatures : config.features.items.map((feature) => feature.split(' - ')[0]).join('  •  ')}
          </p>
        </div>

        {/* CTA Buttons */}
        <div className={styles.ctaButtons}>
          <a
            href={config.links.installation}
            target="_blank"
            rel="noopener noreferrer"
            className={`${styles.ctaButton} ${styles.ctaButtonPrimary}`}
          >
            {config.modal.ctaButtons.install}
          </a>
          <a
            href={config.links.video}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.ctaButton}
          >
            {config.modal.ctaButtons.video}
          </a>
        </div>
      </div>
    </>
  );
}
