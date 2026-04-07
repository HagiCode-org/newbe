import React from 'react';
import LearningPath from './LearningPath';
import CategoryGrid from './CategoryGrid';
import FeaturedDocsSection from './FeaturedDocsSection';
import styles from './styles.module.css';

/**
 * HomepageContent Component
 *
 * Displays the main homepage content including:
 * - Learning path progression
 * - Content category cards
 * - Featured/highlighted documents
 *
 * This component provides a structured navigation experience
 * for users to discover .NET and cloud-native content.
 */
export default function HomepageContent(): JSX.Element {
  return (
    <div className={styles.container}>
      <LearningPath />
      <CategoryGrid />
      <FeaturedDocsSection />
    </div>
  );
}
