import React from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import MirrorCard from './MirrorCard';
import type { ResolvedMirrorLink } from './config';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const GHPROXY_URL = 'https://ghproxy.com/https://github.com/hagicode-org/hagicode/releases/download/v1/app.zip';
const OFFICIAL_URL = 'https://github.com/hagicode-org/hagicode/releases/download/v1/app.zip';

const recommendedMirror: ResolvedMirrorLink = {
  id: 'ghproxy',
  providerKey: 'ghproxy',
  name: 'ghproxy.com',
  icon: '🚀',
  priority: 'recommended',
  recommendationTier: 'standard',
  description: '稳定高速',
  source: 'ghproxy',
  order: 1,
  fullUrl: GHPROXY_URL,
  recommended: true,
  sourceLabel: 'ghproxy',
};

const officialMirror: ResolvedMirrorLink = {
  id: 'official',
  providerKey: 'official',
  name: 'GitHub 原始地址',
  icon: '🔗',
  priority: 'official',
  recommendationTier: 'standard',
  description: '官方源',
  source: 'official',
  order: 900,
  fullUrl: OFFICIAL_URL,
  recommended: false,
  sourceLabel: 'GitHub',
};

type FakePostHog = {
  __loaded: boolean;
  capture: ReturnType<typeof vi.fn>;
  has_opted_out_capturing: ReturnType<typeof vi.fn>;
};

let root: Root | null = null;
let container: HTMLDivElement | null = null;
let fakePostHog: FakePostHog;

function setWindowPostHog(ph: FakePostHog | undefined) {
  if (ph) {
    (window as unknown as { posthog?: FakePostHog }).posthog = ph;
  } else {
    delete (window as unknown as { posthog?: FakePostHog }).posthog;
  }
}

async function renderCard(mirror: ResolvedMirrorLink, onCopy: (url: string) => Promise<void>) {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  await act(async () => {
    root!.render(<MirrorCard mirror={mirror} onCopy={onCopy} />);
  });
}

function button(label: string): HTMLButtonElement {
  const el = container!.querySelector<HTMLButtonElement>(`button[aria-label="${label}"]`);
  if (!el) throw new Error(`button not found: ${label}`);
  return el;
}

async function click(el: HTMLElement) {
  await act(async () => {
    el.click();
  });
}

beforeEach(() => {
  fakePostHog = {
    __loaded: true,
    capture: vi.fn(),
    has_opted_out_capturing: vi.fn(() => false),
  };
  setWindowPostHog(fakePostHog);
  vi.spyOn(window, 'open').mockImplementation(() => null);
});

afterEach(async () => {
  if (root) {
    await act(async () => {
      root!.unmount();
    });
  }
  container?.remove();
  root = null;
  container = null;
  setWindowPostHog(undefined);
  vi.restoreAllMocks();
});

describe('MirrorCard download_mirror_clicked', () => {
  it('sends one copy event for a recommended mirror after the clipboard write resolves', async () => {
    const onCopy = vi.fn(async () => undefined);
    await renderCard(recommendedMirror, onCopy);
    await click(button('复制 ghproxy.com 链接'));

    expect(onCopy).toHaveBeenCalledWith(GHPROXY_URL);
    expect(fakePostHog.capture).toHaveBeenCalledTimes(1);
    expect(fakePostHog.capture).toHaveBeenCalledWith('download_mirror_clicked', {
      mirror: 'ghproxy',
      action: 'copy',
      recommended: true,
    });
  });

  it('sends one open event for a non-recommended mirror and still opens the link', async () => {
    const onCopy = vi.fn(async () => undefined);
    await renderCard(officialMirror, onCopy);
    await click(button('在 GitHub 原始地址 打开链接'));

    expect(window.open).toHaveBeenCalledWith(OFFICIAL_URL, '_blank', 'noopener,noreferrer');
    expect(fakePostHog.capture).toHaveBeenCalledTimes(1);
    expect(fakePostHog.capture).toHaveBeenCalledWith('download_mirror_clicked', {
      mirror: 'official',
      action: 'open',
      recommended: false,
    });
  });

  it('sends an open event with recommended true for a recommended mirror', async () => {
    await renderCard(recommendedMirror, vi.fn(async () => undefined));
    await click(button('在 ghproxy.com 打开链接'));

    expect(fakePostHog.capture).toHaveBeenCalledWith('download_mirror_clicked', {
      mirror: 'ghproxy',
      action: 'open',
      recommended: true,
    });
  });

  it('sends a copy event with recommended false for a non-recommended mirror', async () => {
    await renderCard(officialMirror, vi.fn(async () => undefined));
    await click(button('复制 GitHub 原始地址 链接'));

    expect(fakePostHog.capture).toHaveBeenCalledWith('download_mirror_clicked', {
      mirror: 'official',
      action: 'copy',
      recommended: false,
    });
  });

  it('sends no event when the clipboard write is rejected', async () => {
    const onCopy = vi.fn(async () => {
      throw new Error('denied');
    });
    await renderCard(recommendedMirror, onCopy);
    await click(button('复制 ghproxy.com 链接'));

    expect(onCopy).toHaveBeenCalledTimes(1);
    expect(fakePostHog.capture).not.toHaveBeenCalled();
  });

  it('never puts the full URL or any URL text in an event property', async () => {
    const onCopy = vi.fn(async () => undefined);
    await renderCard(recommendedMirror, onCopy);
    await click(button('复制 ghproxy.com 链接'));
    await click(button('在 ghproxy.com 打开链接'));

    expect(fakePostHog.capture).toHaveBeenCalledTimes(2);
    for (const [, properties] of fakePostHog.capture.mock.calls as Array<[string, Record<string, unknown>]>) {
      expect(Object.keys(properties).sort()).toEqual(['action', 'mirror', 'recommended']);
      for (const value of Object.values(properties)) {
        expect(value).not.toBe(GHPROXY_URL);
        if (typeof value === 'string') {
          expect(value).not.toContain('http');
          expect(value).not.toContain('github.com');
        }
      }
    }
  });

  it('keeps copy and open working when PostHog is unavailable', async () => {
    setWindowPostHog(undefined);
    const onCopy = vi.fn(async () => undefined);
    await renderCard(recommendedMirror, onCopy);
    await click(button('复制 ghproxy.com 链接'));
    await click(button('在 ghproxy.com 打开链接'));

    expect(onCopy).toHaveBeenCalledWith(GHPROXY_URL);
    expect(window.open).toHaveBeenCalledWith(GHPROXY_URL, '_blank', 'noopener,noreferrer');
  });
});
