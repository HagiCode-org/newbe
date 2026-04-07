/**
 * MirrorSection Component - Group container for mirror cards
 * Displays a section with title, icon, and child mirror cards
 */

import React from 'react';
import type { MirrorSectionProps } from './types';
import styles from './styles.module.css';

const MirrorSection: React.FC<MirrorSectionProps> = ({
  title,
  icon,
  children,
  className = '',
}) => {
  return (
    <section className={`${styles.section} ${className}`} aria-label={title}>
      <h3 className={styles.sectionTitle}>
        <span className={styles.sectionIcon} aria-hidden="true">{icon}</span>
        {title}
      </h3>
      <div className={styles.sectionDivider} aria-hidden="true" />
      <div className={styles.sectionContent}>
        {children}
      </div>
    </section>
  );
};

export default MirrorSection;
