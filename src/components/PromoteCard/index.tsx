import React, { useEffect, useState } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

import { loadFirstActivePromotion, type ActivePromotion } from '@site/src/lib/promote-loader';
import styles from './index.module.css';

type PromoteCardProps = {
  fetchImpl?: typeof fetch;
  footerSelector?: string;
};

const DEFAULT_FOOTER_SELECTOR = 'footer, [data-footer-root], .footer';
const DISMISSED_PROMOTIONS_STORAGE_KEY = 'hagicode:promote-card:dismissed-signature';

function ctaLabel(locale: string) {
  return locale.toLowerCase().startsWith('zh') ? '立刻前往' : 'GO';
}

function closeLabel(locale: string) {
  return locale.toLowerCase().startsWith('zh') ? '关闭推广信息' : 'Dismiss promotion';
}

function readDismissedSignature(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage.getItem(DISMISSED_PROMOTIONS_STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeDismissedSignature(signature: string): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(DISMISSED_PROMOTIONS_STORAGE_KEY, signature);
  } catch {
    // Ignore unavailable storage; closing still works for this render.
  }
}

export default function PromoteCard({ fetchImpl, footerSelector = DEFAULT_FOOTER_SELECTOR }: PromoteCardProps) {
  const { i18n } = useDocusaurusContext();
  const locale = i18n.currentLocale ?? 'en';
  const [promotion, setPromotion] = useState<ActivePromotion | null>(null);
  const [footerVisible, setFooterVisible] = useState(false);
  const [dismissedSignature, setDismissedSignature] = useState<string | null>(() => readDismissedSignature());

  useEffect(() => {
    let cancelled = false;
    void loadFirstActivePromotion({ locale, fetchImpl }).then((nextPromotion) => {
      if (!cancelled) setPromotion(nextPromotion);
    });
    return () => {
      cancelled = true;
    };
  }, [fetchImpl, locale]);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof document === 'undefined' || !('IntersectionObserver' in window)) {
      return;
    }

    const footer = document.querySelector<HTMLElement>(footerSelector);
    if (!footer) return;

    const observer = new IntersectionObserver(
      ([entry]) => setFooterVisible(Boolean(entry?.isIntersecting)),
      { threshold: 0.01 },
    );
    observer.observe(footer);
    return () => observer.disconnect();
  }, [footerSelector]);

  const promotionSignature = promotion?.id ?? null;
  const dismissed = Boolean(promotionSignature && dismissedSignature === promotionSignature);

  if (!promotion || footerVisible || dismissed) return null;

  const openPromotion = () => {
    window.open(promotion.link, '_blank', 'noopener,noreferrer');
  };

  const dismissPromotion = () => {
    if (!promotionSignature) return;
    writeDismissedSignature(promotionSignature);
    setDismissedSignature(promotionSignature);
  };

  return (
    <section className={styles.promoteCard} data-promote-card aria-label={locale.toLowerCase().startsWith('zh') ? '推广信息' : 'Promotion'}>
      <button type="button" className={styles.close} onClick={dismissPromotion} aria-label={closeLabel(locale)}>
        <span aria-hidden="true">×</span>
      </button>
      <button type="button" className={styles.surface} onClick={openPromotion} aria-label={`${ctaLabel(locale)}: ${promotion.title}`}>
        <span className={styles.body}>
          <span className={styles.badge}>{promotion.platform ?? 'Promoted'}</span>
          <span className={styles.title}>{promotion.title}</span>
          <span className={styles.description}>{promotion.description}</span>
        </span>
        <span className={styles.cta} aria-hidden="true">{ctaLabel(locale)}</span>
      </button>
    </section>
  );
}
