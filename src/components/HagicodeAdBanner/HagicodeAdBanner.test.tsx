import React from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import { afterEach, describe, expect, it } from 'vitest';
import HagicodeAdBanner from './index';

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
  sessionStorage.clear();
});

describe('HagicodeAdBanner CTA tracking attributes', () => {
  it('marks the install and video links with gaEventAttributes', async () => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
    await act(async () => {
      root!.render(<HagicodeAdBanner />);
    });

    const links = Array.from(container.querySelectorAll<HTMLAnchorElement>('a'));
    expect(links).toHaveLength(2);

    const [install, video] = links;
    expect(install.getAttribute('data-ga-category')).toBe('promotion');
    expect(install.getAttribute('data-ga-label')).toBe('hagicode_ad_banner_install');
    expect(install.getAttribute('data-ga-location')).toBe('header');

    expect(video.getAttribute('data-ga-category')).toBe('promotion');
    expect(video.getAttribute('data-ga-label')).toBe('hagicode_ad_banner_video');
    expect(video.getAttribute('data-ga-location')).toBe('header');
  });
});
