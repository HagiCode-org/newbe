/**
 * QRCodeModal Component - WeChat public account QR code display
 * Shows expandable QR code for alternative download method
 */

import React from 'react';
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

  return (
    <div className={`${styles.qrModal} ${visible ? styles.qrModalVisible : ''} ${className}`}>
      <div className={styles.qrModalContent}>
        <button
          className={styles.qrModalClose}
          onClick={onClose}
          aria-label="关闭二维码"
          type="button"
        >
          ✕
        </button>
        <h4 className={styles.qrModalTitle}>微信公众号</h4>
        <p className={styles.qrModalDescription}>
          如果加速链接失效，关注公众号回复"加速"获取稳定下载地址
        </p>
        <img
          src="/images/weixin_public.png"
          alt="微信公众号二维码"
          className={styles.qrModalImage}
        />
      </div>
    </div>
  );
};

export default QRCodeModal;
