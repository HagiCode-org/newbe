import React, { useState, useEffect } from 'react';
import styles from './index.module.css';
import { HagicodeConfig, HAGICODE_CONFIG } from '../HagicodeConfig';

interface HagicodeAdBannerProps {
  config?: HagicodeConfig;
}

const DISMISSAL_STORAGE_KEY = 'hagicode_header_ad_dismissed';

/**
 * HagicodeAdBanner Component - Gamified Redesign
 *
 * Full-width banner advertisement with animated gradient effects,
 * particle background, and interactive dismiss animation.
 *
 * Features:
 * - Animated gradient background with mesh effect
 * - Floating particle system
 * - Glassmorphism card design
 * - Smooth dismiss animation
 * - Enhanced CTA buttons with glow effects
 */
export default function HagicodeAdBanner({ config = HAGICODE_CONFIG }: HagicodeAdBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Check if banner was dismissed in current session
    try {
      const dismissed = sessionStorage.getItem(DISMISSAL_STORAGE_KEY);
      if (dismissed === 'true') {
        setIsDismissed(true);
      }
    } catch (error) {
      console.warn('sessionStorage not available:', error);
    }
  }, []);

  const handleDismiss = () => {
    setIsExiting(true);
    // Wait for animation to complete before hiding
    setTimeout(() => {
      try {
        sessionStorage.setItem(DISMISSAL_STORAGE_KEY, 'true');
        setIsDismissed(true);
      } catch (error) {
        console.warn('Unable to write to sessionStorage:', error);
      }
    }, 300);
  };

  // Don't render if dismissed
  if (isDismissed) {
    return null;
  }

  return (
    <div className={`${styles.bannerContainer} ${isExiting ? styles.bannerExiting : ''}`}>
      {/* Animated mesh gradient background */}
      <div className={styles.meshGradient} aria-hidden="true">
        <div className={styles.gradientBlob1}></div>
        <div className={styles.gradientBlob2}></div>
        <div className={styles.gradientBlob3}></div>
      </div>

      {/* Particle overlay */}
      <div className={styles.particleOverlay} aria-hidden="true">
        {Array.from({ length: 15 }).map((_, i) => (
          <span
            key={i}
            className={styles.particle}
            style={{
              '--delay': `${i * 0.3}s`,
              '--x': `${Math.random() * 100}%`,
              '--y': `${Math.random() * 100}%`,
              '--duration': `${3 + Math.random() * 4}s`,
            } as React.CSSProperties}
          ></span>
        ))}
      </div>

      {/* Grid pattern overlay */}
      <div className={styles.gridPattern} aria-hidden="true"></div>

      {/* Shine effect on hover */}
      <div className={styles.shineEffect} aria-hidden="true"></div>

      {/* Main content */}
      <div className={styles.bannerInner}>
        {/* Close button */}
        <button
          className={styles.closeButton}
          onClick={handleDismiss}
          aria-label="关闭广告"
          type="button"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>

        {/* Content */}
        <div className={styles.bannerContent}>
          {/* Icon section */}
          <div className={styles.iconSection}>
            <div className={styles.iconWrapper}>
              <span className={styles.icon}>⚡</span>
              <div className={styles.iconPulse}></div>
              <div className={styles.iconPulse2}></div>
            </div>
            <div className={styles.glowOrb}></div>
          </div>

          {/* Text section */}
          <div className={styles.textSection}>
            <h3 className={styles.title}>
              <span className={styles.titleHighlight}>{config.name}</span>
              <span className={styles.titleDash}>—</span>
              <span className={styles.titleText}>{config.tagline}</span>
            </h3>
          </div>

          {/* CTA section */}
          <div className={styles.ctaSection}>
            <a
              href={config.links.installation}
              target="_blank"
              rel="noopener noreferrer"
              className={`${styles.ctaButton} ${styles.ctaPrimary}`}
              aria-label={`${config.modal.ctaButtons.install} - opens in new tab`}
            >
              <span className={styles.ctaText}>{config.modal.ctaButtons.install}</span>
              <span className={styles.ctaGlow}></span>
              <svg className={styles.ctaIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
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
              <svg className={styles.playIcon} width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5,3 19,12 5,21"/>
              </svg>
              <span>{config.modal.ctaButtons.video}</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
