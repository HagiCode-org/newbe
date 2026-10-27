import { afterEach, describe, expect, it, vi } from 'vitest';
import { SITE_EVENT_STRING_MAX_LENGTH, SITE_POSTHOG_EVENTS, captureSiteEvent } from './posthog-events';

const FORBIDDEN_SUPER_KEYS = ['site_id', 'site_framework', 'hagilight_version', 'locale', 'page_type'];
const EVENT_NAME = 'download_mirror_clicked';

function fakePostHog(options: { loaded?: boolean; optedOut?: boolean; throws?: boolean } = {}) {
  const capture = vi.fn(() => {
    if (options.throws) throw new Error('capture failed');
  });
  const hasOptedOut = vi.fn(() => options.optedOut === true);
  return {
    __loaded: options.loaded ?? true,
    capture,
    has_opted_out_capturing: hasOptedOut,
  };
}

afterEach(() => {
  delete (window as unknown as { posthog?: unknown }).posthog;
});

describe('captureSiteEvent', () => {
  it('sends an allowlisted event with the allowed properties', () => {
    const ph = fakePostHog();
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true }, { posthog: ph });
    expect(ph.capture).toHaveBeenCalledTimes(1);
    expect(ph.capture).toHaveBeenCalledWith(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true });
  });

  it('sends nothing for an event name that is not in the table', () => {
    const ph = fakePostHog();
    captureSiteEvent('not_in_table', { mirror: 'ghproxy' }, { posthog: ph });
    captureSiteEvent('constructor', {}, { posthog: ph });
    expect(ph.capture).not.toHaveBeenCalled();
  });

  it('drops keys that are not in the event allowlist', () => {
    const ph = fakePostHog();
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'open', recommended: false, fullUrl: 'https://x.test/a' }, { posthog: ph });
    const sent = ph.capture.mock.calls[0][1] as Record<string, unknown>;
    expect(sent).not.toHaveProperty('fullUrl');
    expect(Object.keys(sent).sort()).toEqual(['action', 'mirror', 'recommended']);
  });

  it('drops values that are not the declared primitive kind', () => {
    const ph = fakePostHog();
    captureSiteEvent(
      EVENT_NAME,
      { mirror: { nested: 1 }, action: ['copy'], recommended: 'true' },
      { posthog: ph },
    );
    expect(ph.capture).toHaveBeenCalledWith(EVENT_NAME, {});
  });

  it('drops enum values outside the declared list', () => {
    const ph = fakePostHog();
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'free text', recommended: true }, { posthog: ph });
    const sent = ph.capture.mock.calls[0][1] as Record<string, unknown>;
    expect(sent).not.toHaveProperty('action');
    expect(sent).toEqual({ mirror: 'ghproxy', recommended: true });
  });

  it('caps string values at 128 characters', () => {
    const ph = fakePostHog();
    captureSiteEvent(EVENT_NAME, { mirror: 'x'.repeat(300), action: 'copy', recommended: false }, { posthog: ph });
    const sent = ph.capture.mock.calls[0][1] as Record<string, string>;
    expect(SITE_EVENT_STRING_MAX_LENGTH).toBe(128);
    expect(sent.mirror).toHaveLength(128);
  });

  it('drops hagilight super-property keys supplied by the caller', () => {
    const ph = fakePostHog();
    captureSiteEvent(
      EVENT_NAME,
      { mirror: 'ghproxy', action: 'copy', recommended: true, site_id: 'newbe', site_framework: 'docusaurus', hagilight_version: '0.18.0', locale: 'zh', page_type: 'mirror' },
      { posthog: ph },
    );
    const sent = ph.capture.mock.calls[0][1] as Record<string, unknown>;
    for (const key of FORBIDDEN_SUPER_KEYS) expect(sent).not.toHaveProperty(key);
  });

  it('sends nothing when window.posthog is undefined and does not throw', () => {
    expect(() => captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true })).not.toThrow();
  });

  it('reads window.posthog when no posthog option is passed', () => {
    const ph = fakePostHog();
    (window as unknown as { posthog: unknown }).posthog = ph;
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true });
    expect(ph.capture).toHaveBeenCalledTimes(1);
  });

  it('queues on a stub that is not loaded yet, without calling has_opted_out_capturing', () => {
    const ph = fakePostHog({ loaded: false, optedOut: true });
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true }, { posthog: ph });
    expect(ph.capture).toHaveBeenCalledTimes(1);
    expect(ph.has_opted_out_capturing).not.toHaveBeenCalled();
  });

  it('checks opt-out before every send once the SDK is loaded', () => {
    const ph = fakePostHog({ loaded: true, optedOut: false });
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true }, { posthog: ph });
    expect(ph.has_opted_out_capturing).toHaveBeenCalledTimes(1);
    expect(ph.capture).toHaveBeenCalledTimes(1);
  });

  it('sends nothing when the visitor has opted out', () => {
    const ph = fakePostHog({ loaded: true, optedOut: true });
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true }, { posthog: ph });
    expect(ph.capture).not.toHaveBeenCalled();
  });

  it('sends nothing when isAllowed returns false', () => {
    const ph = fakePostHog();
    captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true }, { posthog: ph, isAllowed: () => false });
    expect(ph.capture).not.toHaveBeenCalled();
  });

  it('returns normally when capture throws', () => {
    const ph = fakePostHog({ throws: true });
    expect(() => captureSiteEvent(EVENT_NAME, { mirror: 'ghproxy', action: 'copy', recommended: true }, { posthog: ph })).not.toThrow();
    expect(ph.capture).toHaveBeenCalledTimes(1);
  });
});

describe('SITE_POSTHOG_EVENTS table', () => {
  it('names every event snake_case with the object first and uses no forbidden property key', () => {
    for (const [name, props] of Object.entries(SITE_POSTHOG_EVENTS)) {
      expect(name).toMatch(/^[a-z]+(_[a-z]+)+$/);
      for (const key of Object.keys(props)) {
        expect(FORBIDDEN_SUPER_KEYS).not.toContain(key);
      }
    }
  });

  it('sends exactly the allowlisted property set for every event, even with URL, free text and super-property input', () => {
    for (const [name, props] of Object.entries(SITE_POSTHOG_EVENTS)) {
      const valid: Record<string, unknown> = {};
      for (const [key, spec] of Object.entries(props)) {
        switch (spec.kind) {
          case 'string':
            valid[key] = 'value';
            break;
          case 'boolean':
            valid[key] = true;
            break;
          case 'count':
            valid[key] = 3;
            break;
          case 'enum':
            valid[key] = spec.values[0];
            break;
        }
      }
      const noisy = {
        ...valid,
        fullUrl: 'https://ghproxy.com/https://github.com/owner/repo/releases/download/v1/app.exe',
        url: 'https://example.com/path?q=secret#frag',
        note: 'free text the visitor typed',
        site_id: 'newbe',
        site_framework: 'docusaurus',
        hagilight_version: '0.18.0',
        locale: 'zh',
        page_type: 'mirror',
      };
      const ph = fakePostHog();
      captureSiteEvent(name, noisy, { posthog: ph });
      expect(ph.capture).toHaveBeenCalledTimes(1);
      const [sentName, sent] = ph.capture.mock.calls[0] as unknown as [string, Record<string, unknown>];
      expect(sentName).toBe(name);
      expect(Object.keys(sent).sort()).toEqual(Object.keys(props).sort());
      for (const value of Object.values(sent)) {
        if (typeof value === 'string') expect(value).not.toMatch(/https?:\/\//);
      }
    }
  });
});
