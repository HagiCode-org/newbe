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
 *   oneDriveSupport={true}
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
import QRCodeModal from './QRCodeModal';
import HagicodeRecommendation from '../HagicodeRecommendation';

// Configuration
import {
  officialSource,
  recommendedMirrors,
  backupMirrors,
  getMirrorUrl,
} from './config';

const GithubMirrorLink: React.FC<GithubMirrorLinkProps> = ({
  text,
  link,
  oneDriveSupport = false,
}) => {
  // State management
  const [showPopup, setShowPopup] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [toast, setToast] = useState<ToastState>({ visible: false, message: '' });
  const popupRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLAnchorElement>(null);

  // Close popup on ESC key
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      if (showQRModal) {
        setShowQRModal(false);
      } else if (showPopup) {
        setShowPopup(false);
        triggerRef.current?.focus();
      }
    }
  }, [showPopup, showQRModal]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    if (!showPopup && !showQRModal) {
      return undefined;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [showPopup, showQRModal]);

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

  const handleToggleQRModal = () => {
    setShowQRModal(!showQRModal);
  };

  return (
    <div>
      {/* Trigger Link */}
      <a
        ref={triggerRef}
        href="#"
        className={styles.triggerLink}
        onClick={handleClick}
        aria-label={`选择下载方式: ${text}`}
        role="button"
        tabIndex={0}
      >
        {text}
      </a>

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

                  {/* Other Methods Section */}
                  {oneDriveSupport && (
                    <div className={styles.otherMethods}>
                      <p className={styles.otherMethodsText}>
                        如加速链接失效，关注公众号回复"加速"获取稳定下载地址
                      </p>
                      <button
                        className={styles.qrToggleButton}
                        onClick={handleToggleQRModal}
                        type="button"
                      >
                        查看公众号二维码
                      </button>
                    </div>
                  )}
                </aside>

                <div className={styles.contentMain}>
                  {/* Official Source Section */}
                  <MirrorSection title="官方源" icon="🔗">
                    <MirrorCard
                      mirror={officialSource}
                      fullUrl={link}
                      onCopy={copyToClipboard}
                    />
                  </MirrorSection>

                  {/* Recommended Mirrors Section */}
                  <MirrorSection title="推荐加速器" icon="⭐">
                    {recommendedMirrors.map((mirror) => (
                      <MirrorCard
                        key={mirror.id}
                        mirror={mirror}
                        fullUrl={getMirrorUrl(mirror, link)}
                        onCopy={copyToClipboard}
                      />
                    ))}
                  </MirrorSection>

                  {/* Backup Mirrors Section */}
                  <MirrorSection title="备用加速器" icon="📦">
                    {backupMirrors.map((mirror) => (
                      <MirrorCard
                        key={mirror.id}
                        mirror={mirror}
                        fullUrl={getMirrorUrl(mirror, link)}
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

      {/* QR Code Modal */}
      {showQRModal && (
        <QRCodeModal
          visible={showQRModal}
          onClose={() => setShowQRModal(false)}
        />
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
