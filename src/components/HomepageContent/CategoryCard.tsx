import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import { Category as CategoryType } from './config';

interface CategoryCardProps {
  category: CategoryType;
}

// SVG icon components using Heroicons
const Icons = {
  mic: (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M11.25 4.533A9.707 9.707 0 006 3a9.735 9.735 0 00-3.25.555.75.75 0 00-.5.707v14.25a.75.75 0 001 .707A8.237 8.237 0 016 18.75c1.995 0 3.823.707 5.25 1.886V4.533zM12.75 20.636A8.214 8.214 0 0118 18.75c.966 0 1.89.166 2.75.47v-14.5a9.735 9.735 0 00-3.25-.555 9.707 9.707 0 00-5.25 1.533v16.103z" />
      <path fillRule="evenodd" d="M12 2.25A6.75 6.75 0 005.25 9v.75h-1.5a.75.75 0 00-.75.75v9c0 4.556 4.03 8.25 9 8.25s9-3.694 9-8.25v-9a.75.75 0 00-.75-.75h-1.5V9A6.75 6.75 0 0012 2.25zm0 9a2.25 2.25 0 100-4.5 2.25 2.25 0 000 4.5z" clipRule="evenodd" />
    </svg>
  ),
  mirrors: (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M1.5 6a2.25 2.25 0 012.25-2.25h16.5A2.25 2.25 0 0122.5 6v12a2.25 2.25 0 01-2.25 2.25H3.75A2.25 2.25 0 011.5 18V6zM3 16.06V18c0 .414.336.75.75.75h16.5A.75.75 0 0021 18v-1.94l-2.69-2.689a1.5 1.5 0 00-2.12 0l-.88.879.97.97a.75.75 0 11-1.06 1.06l-5.16-5.159a1.5 1.5 0 00-2.12 0L3 16.061zm10.125-7.81a1.125 1.125 0 112.25 0 1.125 1.125 0 01-2.25 0z" clipRule="evenodd" />
    </svg>
  ),
  tutorial: (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M11.25 4.533A9.707 9.707 0 006 3a9.735 9.735 0 00-3.25.555.75.75 0 00-.5.707v14.25a.75.75 0 001 .707A8.237 8.237 0 016 18.75c1.995 0 3.823.707 5.25 1.886V4.533zM12.75 20.636A8.214 8.214 0 0118 18.75c.966 0 1.89.166 2.75.47v-14.5a9.735 9.735 0 00-3.25-.555 9.707 9.707 0 00-5.25 1.533v16.103z" clipRule="evenodd" />
    </svg>
  ),
  projects: (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813a3.75 3.75 0 002.576-2.576l.813-2.846A.75.75 0 019 4.5zM3.75 13.5a.75.75 0 01.75-.75H9a.75.75 0 010 1.5H4.5a.75.75 0 01-.75-.75zM3.75 18a.75.75 0 01.75-.75H9a.75.75 0 010 1.5H4.5a.75.75 0 01-.75-.75z" clipRule="evenodd" />
    </svg>
  ),
} as const;

export default function CategoryCard({ category }: CategoryCardProps): JSX.Element {
  const iconSvg = Icons[category.id as keyof typeof Icons] || Icons.projects;

  return (
    <Link
      to={category.link}
      className={styles.categoryCard}
      aria-label={`浏览${category.title}分类`}
    >
      <div className={styles.categoryCardHeader}>
        <span className={styles.categoryCardIcon}>{iconSvg}</span>
        <h3 className={styles.categoryCardTitle}>{category.title}</h3>
      </div>
      <p className={styles.categoryCardDescription}>{category.description}</p>
      <div className={styles.categoryCardDocsTitle}>精选内容</div>
      <ul className={styles.categoryCardDocsList}>
        {category.featuredDocs.map((doc, index) => (
          <li key={index} className={styles.categoryCardDocsItem}>
            {doc.title}
          </li>
        ))}
      </ul>
      <span className={styles.categoryCardLink}>浏览全部</span>
    </Link>
  );
}
