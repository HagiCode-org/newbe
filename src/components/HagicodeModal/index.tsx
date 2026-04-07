import React, { useEffect } from 'react';
import styles from './index.module.css';
import { HagicodeConfig, HAGICODE_CONFIG, markTodayVisited } from '../HagicodeConfig';

interface HagicodeModalProps {
  isOpen?: boolean;
  config?: HagicodeConfig;
  onClose?: () => void;
}

/**
 * HagicodeModal Component
 *
 * Displays a promotional modal for Hagicode product on first daily visit.
 * Uses localStorage to track and limit display frequency.
 *
 * Features:
 * - Shows only once per day
 * - Closing the modal marks today as visited
 * - Multiple close methods: X button, ESC key, backdrop click
 * - Responsive design with mobile bottom-sheet behavior
 * - Glassmorphism design with modern color palette
 * - Accessibility: focus management, keyboard navigation, ARIA attributes
 */
export default function HagicodeModal({ isOpen = false, config = HAGICODE_CONFIG, onClose }: HagicodeModalProps) {
  const backdropRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Prevent body scroll when modal is open
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isOpen]);

  useEffect(() => {
    // Handle ESC key press
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    // Trap focus within modal when open
    const handleTabKey = (event: KeyboardEvent) => {
      if (!isOpen || event.key !== 'Tab') return;

      const focusableElements = backdropRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (focusableElements && focusableElements.length > 0) {
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscKey);
      document.addEventListener('keydown', handleTabKey);
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
      document.removeEventListener('keydown', handleTabKey);
    };
  }, [isOpen]);

  const handleClose = () => {
    // Mark today as visited when modal is closed
    markTodayVisited();

    if (onClose) {
      onClose();
    }
  };

  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div
      ref={backdropRef}
      className={styles.modal}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="hagicode-modal-title"
      aria-describedby="hagicode-modal-description"
    >
      <div className={styles.modalContent}>
        {/* Header with close button */}
        <div className={styles.header}>
          <button
            className={styles.closeButton}
            onClick={handleClose}
            aria-label="关闭弹窗"
            type="button"
          >
            ×
          </button>
        </div>

        {/* Body content */}
        <div className={styles.body}>
          {/* Title section */}
          <div className={styles.titleSection}>
            <div className={styles.titleIcon} aria-hidden="true">⚡</div>
            <h2 id="hagicode-modal-title" className={styles.title}>
              {config.name}
            </h2>
            <p className={styles.tagline}>{config.tagline}</p>
          </div>

          {/* Description */}
          <p id="hagicode-modal-description" className={styles.description}>
            {config.description}
          </p>

          {/* Features list */}
          <ul className={styles.features} aria-label="核心功能">
            {config.features.items.map((feature, index) => (
              <li key={index} className={styles.featureItem}>
                {feature}
              </li>
            ))}
          </ul>

          {/* CTA buttons */}
          <div className={styles.ctaButtons}>
            <a
              href={config.links.installation}
              target="_blank"
              rel="noopener noreferrer"
              className={`${styles.ctaButton} ${styles.ctaButtonPrimary}`}
              aria-label={`${config.modal.ctaButtons.install} - 将在新标签页打开`}
            >
              {config.modal.ctaButtons.install}
            </a>
            <a
              href={config.links.video}
              target="_blank"
              rel="noopener noreferrer"
              className={`${styles.ctaButton} ${styles.ctaButtonSecondary}`}
              aria-label={`${config.modal.ctaButtons.video} - 将在新标签页打开`}
            >
              {config.modal.ctaButtons.video}
            </a>
          </div>

          {/* Footer URL */}
          <div className={styles.footerUrl}>
            <p className={styles.footerUrlText}>{config.links.homepage}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
