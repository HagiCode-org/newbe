import React from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import { afterEach, describe, expect, it } from 'vitest';
import HagicodeRecommendation from './index';

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
});

async function render(layout: 'page' | 'modal') {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  await act(async () => {
    root!.render(<HagicodeRecommendation layout={layout} />);
  });
  return Array.from(container.querySelectorAll<HTMLAnchorElement>('a'));
}

describe('HagicodeRecommendation CTA tracking attributes', () => {
  it('marks the install and video links on the page layout as article promotions', async () => {
    const [install, video] = await render('page');
    expect(install.getAttribute('data-ga-category')).toBe('promotion');
    expect(install.getAttribute('data-ga-label')).toBe('hagicode_recommendation_install');
    expect(install.getAttribute('data-ga-location')).toBe('article_promotion');
    expect(video.getAttribute('data-ga-category')).toBe('promotion');
    expect(video.getAttribute('data-ga-label')).toBe('hagicode_recommendation_video');
    expect(video.getAttribute('data-ga-location')).toBe('article_promotion');
  });

  it('marks the install and video links in the modal layout as mirror popup promotions', async () => {
    const [install, video] = await render('modal');
    expect(install.getAttribute('data-ga-category')).toBe('promotion');
    expect(install.getAttribute('data-ga-label')).toBe('hagicode_recommendation_install');
    expect(install.getAttribute('data-ga-location')).toBe('mirror_popup');
    expect(video.getAttribute('data-ga-category')).toBe('promotion');
    expect(video.getAttribute('data-ga-label')).toBe('hagicode_recommendation_video');
    expect(video.getAttribute('data-ga-location')).toBe('mirror_popup');
  });
});
