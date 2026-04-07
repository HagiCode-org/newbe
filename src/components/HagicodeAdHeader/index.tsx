import React from 'react';
import styles from './index.module.css';
import { HagicodeConfig, HAGICODE_CONFIG } from '../HagicodeConfig';

interface HagicodeAdHeaderProps {
  config?: HagicodeConfig;
}

/**
 * HagicodeAdHeader Component - Gamified Redesign
 *
 * Compact inline advertisement with animated glow effects,
 * glassmorphism, and interactive hover states.
 *
 * Features:
 * - Animated glow border with pulse effect
 * - Glassmorphism with backdrop blur
 * - Floating particle animation
 * - Shine effect on hover
 * - Dynamic lighting simulation
 */
export default function HagicodeAdHeader({ config = HAGICODE_CONFIG }: HagicodeAdHeaderProps) {
  return (
    <div className={styles.headerAdContainer}>
      {/* Animated glow effect */}
      <div className={styles.glowEffect} aria-hidden="true"></div>
      <div className={styles.glowEffectSecondary} aria-hidden="true"></div>

      {/* Floating particles */}
      <div className={styles.particles} aria-hidden="true">
        <span className={styles.particle}></span>
        <span className={styles.particle}></span>
        <span className={styles.particle}></span>
      </div>

      {/* Shine effect layer */}
      <div className={styles.shineLayer} aria-hidden="true"></div>

      {/* Main content */}
      <div className={styles.headerAdInner}>
        <div className={styles.iconWrapper}>
          <span className={styles.icon}>⚡</span>
          <div className={styles.iconRing}></div>
        </div>

        <div className={styles.content}>
          <span className={styles.title}>
            <span className={styles.titleHighlight}>{config.name}</span>
            <span className={styles.titleSeparator}>·</span>
            {config.tagline}
          </span>
        </div>

        <div className={styles.ctaGroup}>
          <a
            href={config.links.installation}
            target="_blank"
            rel="noopener noreferrer"
            className={`${styles.ctaButton} ${styles.ctaPrimary}`}
            aria-label={`${config.modal.ctaButtons.install} - opens in new tab`}
          >
            <span className={styles.ctaButtonText}>{config.modal.ctaButtons.install}</span>
            <span className={styles.ctaButtonGlow}></span>
            <svg className={styles.ctaIcon} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M13 7l5 5m0 0l-5 5m5-5H6"/>
            </svg>
          </a>
          <a
            href={config.links.video}
            target="_blank"
            rel="noopener noreferrer"
            className={`${styles.ctaButton} ${styles.ctaSecondary}`}
            aria-label={`${config.modal.ctaButtons.video} - opens in new tab`}
          >
            <svg className={styles.playIcon} width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5,3 19,12 5,21"/>
            </svg>
            {config.modal.ctaButtons.video}
          </a>
        </div>
      </div>
    </div>
  );
}
