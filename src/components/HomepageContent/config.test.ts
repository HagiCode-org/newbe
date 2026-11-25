import { describe, expect, it } from 'vitest';
import { homepageContent } from './config';

// Pages the site still publishes besides docs/Mirrors (see docs/intro.md and src/pages).
const FIXED_PAGES = ['/links', '/privacy', '/markdown-page'];

describe('homepage content config', () => {
  it('links only to mirror pages or fixed site pages', () => {
    const targets = [
      ...homepageContent.learningPath.map((step) => step.link),
      ...homepageContent.categories.flatMap((category) => [
        category.link,
        ...category.featuredDocs.map((doc) => doc.path),
      ]),
      ...homepageContent.featuredDocs.map((doc) => doc.path),
    ].filter((target): target is string => Boolean(target));

    expect(targets.length).toBeGreaterThan(0);
    for (const target of targets) {
      const isMirror = target === '/Mirrors' || target.startsWith('/Mirrors/');
      expect(isMirror || FIXED_PAGES.includes(target), target).toBe(true);
    }
  });

  it('keeps only the mirrors category', () => {
    expect(homepageContent.categories.map((category) => category.id)).toEqual(['mirrors']);
  });
});
