/**
 * GithubMirrorLink Component - Enhanced UI/UX Version
 * Provides users with accelerated download options for GitHub resources
 *
 * Features:
 * - Card-based mirror display with icons and descriptions
 * - Copy to clipboard functionality with Toast feedback
 * - Responsive design for mobile and desktop
 * - Keyboard navigation support (ESC to close, Tab for focus)
 * - Dark theme support via Docusaurus CSS variables
 *
 * @example
 * ```tsx
 * <GithubMirrorLink
 *   text="下载源码"
 *   link="https://github.com/user/repo/archive/refs/heads/main.zip"
 * />
 * ```
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import type { GithubMirrorLinkProps, ToastState } from './types';
import styles from './styles.module.css';

// Sub-components
import MirrorSection from './MirrorSection';
import MirrorCard from './MirrorCard';
import Toast from './Toast';
import HagicodeRecommendation from '../HagicodeRecommendation';

// Configuration
import {
  buildMirrorSections,
  PRIMARY_RECOMMENDED_PROVIDER_KEY,
} from './config';

const GithubMirrorLink: React.FC<GithubMirrorLinkProps> = ({
  text,
  link,
  repositoryKey,
  preferredProviders = [],
  resolvedMirrors = [],
}) => {
  // State management
  const [showPopup, setShowPopup] = useState(false);
  const [toast, setToast] = useState<ToastState>({ visible: false, message: '' });
  const popupRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLAnchorElement>(null);

  // Close popup on ESC key
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      if (showPopup) {
        setShowPopup(false);
        triggerRef.current?.focus();
      }
    }
  }, [showPopup]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    if (!showPopup) {
      return undefined;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [showPopup]);

  // Focus trap for popup
  useEffect(() => {
    if (showPopup && popupRef.current) {
      const focusableElements = popupRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      firstElement?.focus();

      const handleTabKey = (e: KeyboardEvent) => {
        if (e.key === 'Tab') {
          if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement?.focus();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement?.focus();
          }
        }
      };

      document.addEventListener('keydown', handleTabKey);
      return () => document.removeEventListener('keydown', handleTabKey);
    }
  }, [showPopup]);

  // Copy to clipboard with fallback
  const copyToClipboard = useCallback(async (text: string): Promise<void> => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        if (!successful) {
          throw new Error('Copy failed');
        }
      }
      setToast({ visible: true, message: '已复制到剪贴板' });
    } catch (error) {
      console.error('Failed to copy:', error);
      setToast({ visible: true, message: '复制失败，请手动复制' });
    }
  }, []);

  const handleToastHide = useCallback(() => {
    setToast({ visible: false, message: '' });
  }, []);

  const handleClick = (event: React.MouseEvent) => {
    event.preventDefault();
    setShowPopup(true);
  };

  const handleClosePopup = () => {
    setShowPopup(false);
  };

  const handleBackdropClick = (event: React.MouseEvent) => {
    if (event.target === event.currentTarget) {
      handleClosePopup();
    }
  };

  const mirrorSections = buildMirrorSections({
    githubLink: link,
    repositoryKey,
    preferredProviders,
    resolvedMirrors,
  });
  const domesticPanMirror =
    mirrorSections.recommended.find((mirror) => mirror.providerKey === PRIMARY_RECOMMENDED_PROVIDER_KEY) ??
    mirrorSections.backup.find((mirror) => mirror.providerKey === PRIMARY_RECOMMENDED_PROVIDER_KEY);
  const supportsDomesticPanAcceleration = Boolean(domesticPanMirror);

  return (
    <div>
      {/* Trigger Link */}
      <span className={styles.triggerAction}>
        <a
          ref={triggerRef}
          href="#"
          className={styles.triggerLink}
          onClick={handleClick}
          aria-label={
            supportsDomesticPanAcceleration
              ? `选择下载方式: ${text}，支持国内网盘加速下载`
              : `选择下载方式: ${text}`
          }
          role="button"
          tabIndex={0}
        >
          {text}
        </a>
        {supportsDomesticPanAcceleration && (
          <a
            className={styles.triggerDomesticBadge}
            href={domesticPanMirror?.fullUrl}
            target="_blank"
            rel="noopener noreferrer"
            title="打开网盘下载链接"
            aria-label={`打开 ${text} 的网盘下载链接`}
          >
            <span className={styles.triggerDomesticBadgeLabel}>高速网盘下载</span>
          </a>
        )}
      </span>

      {/* Main Popup Modal */}
      {showPopup && typeof document !== 'undefined' && createPortal(
        <div
          className={styles.popup}
          onClick={handleBackdropClick}
          role="dialog"
          aria-modal="true"
          aria-labelledby="mirror-modal-title"
        >
          <div
            ref={popupRef}
            className={styles.popupContent}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className={styles.header}>
              <h2 id="mirror-modal-title" className={styles.title}>
                选择下载方式
              </h2>
              <button
                className={styles.closeButton}
                onClick={handleClosePopup}
                aria-label="关闭"
                type="button"
              >
                ✕
              </button>
            </div>

            {/* Alert Banner */}
            <div className={styles.alertBanner}>
              <span className={styles.alertBannerIcon} aria-hidden="true">
                ⚠
              </span>
              <span>
                加速链接均为互联网上的公开资源，仅供学习交流使用。本站不存储任何资源文件，不提供下载服务。
              </span>
            </div>

            {/* Content */}
            <div className={styles.content}>
              <div className={styles.contentGrid}>
                <aside className={styles.contentSidebar}>
                  {/* Mirror pages and modal share the same Hagicode copy to keep CTA text aligned. */}
                  <div className={styles.promoSection}>
                    <HagicodeRecommendation layout="modal" />
                  </div>
                </aside>

                <div className={styles.contentMain}>
                  {/* Recommended Mirrors Section */}
                  <MirrorSection title="推荐加速器" icon="⭐">
                    {mirrorSections.recommended.map((mirror) => (
                      <MirrorCard
                        key={`${mirror.id}-${mirror.fullUrl}`}
                        mirror={mirror}
                        onCopy={copyToClipboard}
                      />
                    ))}
                  </MirrorSection>

                  {/* Backup Mirrors Section */}
                  <MirrorSection title="备用加速器" icon="📦">
                    {mirrorSections.backup.map((mirror) => (
                      <MirrorCard
                        key={`${mirror.id}-${mirror.fullUrl}`}
                        mirror={mirror}
                        onCopy={copyToClipboard}
                      />
                    ))}
                  </MirrorSection>

                  {/* Official Source Section */}
                  <MirrorSection title="官方源" icon="🔗">
                    {mirrorSections.official.map((mirror) => (
                      <MirrorCard
                        key={`${mirror.id}-${mirror.fullUrl}`}
                        mirror={mirror}
                        onCopy={copyToClipboard}
                      />
                    ))}
                  </MirrorSection>
                </div>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Toast Notification */}
      <Toast
        visible={toast.visible}
        message={toast.message}
        duration={2000}
        onHide={handleToastHide}
      />
    </div>
  );
};

export default GithubMirrorLink;
