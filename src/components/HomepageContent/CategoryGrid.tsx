import React from 'react';
import CategoryCard from './CategoryCard';
import styles from './styles.module.css';
import { homepageContent } from './config';

export default function CategoryGrid(): JSX.Element {
  return (
    <section className={styles.categoryGridSection} aria-label="内容分类">
      <h2 className={styles.sectionTitle}>内容分类</h2>
      <div className={styles.categoryGrid}>
        {homepageContent.categories.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </div>
    </section>
  );
}
