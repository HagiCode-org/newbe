import React from 'react';
import FeaturedDocCard from './FeaturedDocCard';
import styles from './styles.module.css';
import { homepageContent } from './config';

export default function FeaturedDocsSection(): JSX.Element {
  return (
    <section className={styles.featuredDocsSection} aria-label="热门推荐文章">
      <h2 className={styles.sectionTitle}>热门推荐</h2>
      <div className={styles.featuredDocsGrid}>
        {homepageContent.featuredDocs.map((doc, index) => (
          <FeaturedDocCard
            key={index}
            title={doc.title}
            description={doc.description || ''}
            path={doc.path}
            badge={doc.badge}
          />
        ))}
      </div>
    </section>
  );
}
