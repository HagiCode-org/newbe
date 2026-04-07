import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface FeaturedDocCardProps {
  title: string;
  description: string;
  path: string;
  badge?: string;
}

export default function FeaturedDocCard({
  title,
  description,
  path,
  badge,
}: FeaturedDocCardProps): JSX.Element {
  return (
    <Link
      to={path}
      className={styles.featuredDocCard}
      aria-label={`阅读文章: ${title}`}
    >
      {badge && <span className={styles.featuredDocBadge}>{badge}</span>}
      <h3 className={styles.featuredDocTitle}>{title}</h3>
      <p className={styles.featuredDocDescription}>{description}</p>
    </Link>
  );
}
