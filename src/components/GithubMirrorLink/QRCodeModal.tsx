/**
 * QRCodeModal Component - WeChat public account QR code display
 * Shows expandable QR code for alternative download method
 */

import React from 'react';
import { createPortal } from 'react-dom';
import type { QRCodeModalProps } from './types';
import styles from './styles.module.css';

const QRCodeModal: React.FC<QRCodeModalProps> = ({
  visible,
  onClose,
  className = '',
}) => {
  if (!visible) {
    return null;
  }

  if (typeof document === 'undefined') {
    return null;
  }

  return createPortal(
    <div
      className={`${styles.qrModal} ${visible ? styles.qrModalVisible : ''} ${className}`}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="mirror-qr-modal-title"
    >
      <div className={styles.qrModalContent} onClick={(event) => event.stopPropagation()}>
        <button
          className={styles.qrModalClose}
          onClick={onClose}
          aria-label="关闭二维码"
          type="button"
        >
          ✕
        </button>
        <h4 id="mirror-qr-modal-title" className={styles.qrModalTitle}>微信公众号</h4>
        <p className={styles.qrModalDescription}>
          如果加速链接失效，关注公众号回复"加速"获取稳定下载地址
        </p>
        <img
          src="/images/weixin_public.png"
          alt="微信公众号二维码"
          className={styles.qrModalImage}
        />
      </div>
    </div>,
    document.body
  );
};

export default QRCodeModal;
