/**
 * Toast Component - Copy feedback notification
 * Displays a temporary notification message with fade animations
 */

import React, { useEffect } from 'react';
import type { ToastProps } from './types';
import styles from './styles.module.css';

const Toast: React.FC<ToastProps> = ({
  visible,
  message,
  duration = 2000,
  onHide,
}) => {
  useEffect(() => {
    if (visible && duration > 0) {
      const timer = setTimeout(() => {
        onHide?.();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [visible, duration, onHide]);

  if (!visible) {
    return null;
  }

  return (
    <div
      className={styles.toast}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <span className={styles.toastIcon}>✓</span>
      <span className={styles.toastMessage}>{message}</span>
    </div>
  );
};

export default Toast;
