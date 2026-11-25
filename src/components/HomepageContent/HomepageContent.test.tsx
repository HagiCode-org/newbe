import React from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import { afterEach, describe, expect, it, vi } from 'vitest';
import FeaturedDocsSection from './FeaturedDocsSection';
import LearningPath from './LearningPath';

// The homepage components read their lists from this object at render time, so each test
// fills or empties it before rendering.
const content = vi.hoisted(() => ({
  learningPath: [] as Array<{ step: number; title: string; description: string; link?: string }>,
  categories: [] as unknown[],
  featuredDocs: [] as Array<{ title: string; path: string; description?: string; badge?: string }>,
}));

vi.mock('./config', () => ({ homepageContent: content }));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let root: Root | null = null;
let container: HTMLDivElement | null = null;

afterEach(async () => {
  if (root) {
    await act(async () => {
      root!.unmount();
    });
  }
  container?.remove();
  root = null;
  container = null;
  content.learningPath = [];
  content.featuredDocs = [];
});

async function render(element: React.ReactElement): Promise<HTMLDivElement> {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  await act(async () => {
    root!.render(element);
  });
  return container;
}

describe('homepage sections with no entries', () => {
  it('hides the featured section instead of rendering an empty heading', async () => {
    content.featuredDocs = [];
    const host = await render(<FeaturedDocsSection />);
    expect(host.innerHTML).toBe('');
    expect(host.textContent).not.toContain('热门推荐');
  });

  it('hides the learning path section when it has no steps', async () => {
    content.learningPath = [];
    const host = await render(<LearningPath />);
    expect(host.innerHTML).toBe('');
    expect(host.textContent).not.toContain('学习路径');
  });
});

describe('homepage sections with entries', () => {
  it('renders the featured section and links each entry to its path', async () => {
    content.featuredDocs = [{ title: 'Dapr 文档镜像', path: '/Mirrors/Mirrors-Dapr', badge: '🔄 镜像' }];
    const host = await render(<FeaturedDocsSection />);
    expect(host.textContent).toContain('热门推荐');
    const links = Array.from(host.querySelectorAll<HTMLAnchorElement>('a'));
    expect(links.map((link) => link.getAttribute('href'))).toEqual(['/Mirrors/Mirrors-Dapr']);
  });

  it('renders the learning path steps with their links', async () => {
    content.learningPath = [{ step: 1, title: '云原生进阶', description: 'Dapr, K8s, Docker', link: '/Mirrors' }];
    const host = await render(<LearningPath />);
    expect(host.textContent).toContain('学习路径');
    const links = Array.from(host.querySelectorAll<HTMLAnchorElement>('a'));
    expect(links.map((link) => link.getAttribute('href'))).toEqual(['/Mirrors']);
  });
});
