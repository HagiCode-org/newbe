/**
 * MirrorCard Component - Individual mirror link display card
 * Shows mirror name, icon, description, and action buttons
 */

import React, { useState } from 'react';
import type { MirrorCardProps } from './types';
import {
  PRIMARY_RECOMMENDATION_BADGES,
  isPrimaryRecommendedMirror,
} from './config';
import styles from './styles.module.css';

const MirrorCard: React.FC<MirrorCardProps> = ({
  mirror,
  onCopy,
  className = '',
}) => {
  const [copyState, setCopyState] = useState<'idle' | 'copying' | 'success' | 'error'>('idle');
  const isPrimaryRecommendation = isPrimaryRecommendedMirror(mirror);
  const recommendationTier = isPrimaryRecommendation
    ? 'primary'
    : mirror.recommended
      ? 'standard'
      : undefined;

  const handleCopy = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    setCopyState('copying');
    try {
      await onCopy(mirror.fullUrl);
      setCopyState('success');
      setTimeout(() => setCopyState('idle'), 2000);
    } catch {
      setCopyState('error');
      setTimeout(() => setCopyState('idle'), 2000);
    }
  };

  const handleOpen = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    window.open(mirror.fullUrl, '_blank', 'noopener,noreferrer');
  };

  const getCopyButtonText = () => {
    switch (copyState) {
      case 'copying':
        return '复制中...';
      case 'success':
        return '已复制';
      case 'error':
        return '失败';
      default:
        return '复制';
    }
  };

  const getCopyButtonClass = () => {
    const baseClass = styles.cardButton;
    switch (copyState) {
      case 'success':
        return `${baseClass} ${styles.cardButtonSuccess}`;
      case 'error':
        return `${baseClass} ${styles.cardButtonError}`;
      default:
        return baseClass;
    }
  };

  return (
    <div
      className={[
        styles.card,
        isPrimaryRecommendation ? styles.cardPrimaryRecommendation : '',
        className,
      ].filter(Boolean).join(' ')}
      data-provider-key={mirror.providerKey}
      data-recommendation-tier={recommendationTier}
    >
      <div className={styles.cardHeader}>
        <div className={styles.cardTitleSection}>
          <span className={styles.cardIcon} aria-hidden="true">{mirror.icon}</span>
          <div className={styles.cardTitleText}>
            <div className={styles.cardTitleRow}>
              <span className={styles.cardName}>{mirror.name}</span>
              {isPrimaryRecommendation && (
                <span className={styles.cardBadgeGroup}>
                  {PRIMARY_RECOMMENDATION_BADGES.map((badgeText, index) => (
                    <span
                      key={badgeText}
                      className={`${styles.cardBadge} ${index === 0 ? styles.cardBadgePrimary : styles.cardBadgeSecondary}`}
                    >
                      {badgeText}
                    </span>
                  ))}
                </span>
              )}
              {!isPrimaryRecommendation && mirror.recommended && (
                <span className={styles.cardBadge}>推荐</span>
              )}
            </div>
            <span className={styles.cardDescription}>{mirror.description}</span>
            <div className={styles.cardMeta}>
              <span className={styles.cardMetaItem}>来源: {mirror.sourceLabel}</span>
              {mirror.syncedAt && (
                <span className={styles.cardMetaItem}>同步: {mirror.syncedAt}</span>
              )}
            </div>
          </div>
        </div>
        <div className={styles.cardActions}>
          <button
            className={`${styles.cardButton} ${styles.cardButtonPrimary}`}
            onClick={handleOpen}
            aria-label={`在 ${mirror.name} 打开链接`}
            type="button"
          >
            打开
          </button>
          <button
            className={getCopyButtonClass()}
            onClick={handleCopy}
            aria-label={`复制 ${mirror.name} 链接`}
            type="button"
            disabled={copyState === 'copying'}
          >
            {getCopyButtonText()}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MirrorCard;
