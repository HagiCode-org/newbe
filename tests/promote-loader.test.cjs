const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const { pathToFileURL } = require('node:url');

const ts = require('typescript');

const repoRoot = path.resolve(__dirname, '..');
const loaderPath = path.join(repoRoot, 'src/lib/promote-loader.ts');
const jsonHeaders = { 'content-type': 'application/json' };
const BOUNDARY = '2026-04-29T00:00:00+08:00';
const BEFORE_BOUNDARY = '2026-04-28T23:59:59+08:00';
const AFTER_BOUNDARY = '2026-04-29T00:00:01+08:00';

function response(payload, init = {}) {
  return new Response(JSON.stringify(payload), { status: 200, headers: jsonHeaders, ...init });
}

async function loadPromoteLoader() {
  const source = fs.readFileSync(loaderPath, 'utf8');
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ESNext,
      target: ts.ScriptTarget.ES2022,
    },
    fileName: loaderPath,
  });

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'newbe-promote-loader-'));
  const tempFile = path.join(tempDir, 'promote-loader.mjs');
  fs.writeFileSync(tempFile, output.outputText, 'utf8');
  return import(`${pathToFileURL(tempFile).href}?t=${Date.now()}`);
}

function createCatalogFetch(payload) {
  const contents = payload.contents ?? payload.promotes.map((promotion) => ({
    id: promotion.id,
    title: { en: `Title ${promotion.id}`, zh: `标题 ${promotion.id}` },
    description: { en: `Description ${promotion.id}`, zh: `描述 ${promotion.id}` },
    link: `https://example.invalid/${promotion.id}`,
    targetPlatform: 'steam',
    cta: { en: `Open ${promotion.id}`, zh: `打开 ${promotion.id}` },
  }));

  return async (input) => {
    const url = input.toString();
    if (url.endsWith('/index-catalog.json')) {
      return response({
        entries: [
          { id: 'promotion-flags', path: '/promote.json' },
          { id: 'promotion-content', path: '/promote_content.json' },
        ],
      });
    }
    if (url.endsWith('/promote.json')) {
      return response({ promotes: payload.promotes });
    }
    if (url.endsWith('/promote_content.json')) {
      return response({ contents });
    }
    throw new Error(`Unexpected URL: ${url}`);
  };
}

test('newbe promote loader applies the shared schedule semantics', async () => {
  const { loadActivePromotions, loadFirstActivePromotion } = await loadPromoteLoader();

  const fetchImpl = createCatalogFetch({
    promotes: [
      { id: 'main-game-2026-04-29', on: true, endTime: BOUNDARY },
      { id: 'main-game-steam-ea-2026-04-29', on: true, startTime: BOUNDARY },
      { id: 'future', on: true, startTime: AFTER_BOUNDARY },
      { id: 'broken', on: true, startTime: 'not-a-date' },
      { id: 'no-end', on: true, startTime: BEFORE_BOUNDARY },
    ],
  });

  const before = await loadActivePromotions({
    locale: 'en',
    fetchImpl,
    now: Date.parse(BEFORE_BOUNDARY),
  });
  const atBoundary = await loadFirstActivePromotion({
    locale: 'en',
    fetchImpl,
    now: Date.parse(BOUNDARY),
  });

  assert.deepEqual(
    before.map((promotion) => promotion.id),
    ['main-game-2026-04-29', 'no-end'],
  );
  assert.equal(atBoundary?.id, 'main-game-steam-ea-2026-04-29');
  assert.equal(before[0].ctaLabel, 'Open main-game-2026-04-29');
  assert.equal(atBoundary?.ctaLabel, 'Open main-game-steam-ea-2026-04-29');
});

test('newbe promote loader resolves CTA labels with shared fallbacks', async () => {
  const { loadActivePromotions } = await loadPromoteLoader();

  const fetchImpl = createCatalogFetch({
    promotes: [
      { id: 'localized', on: true },
      { id: 'missing-locale', on: true },
      { id: 'malformed-cta', on: true },
      { id: 'legacy', on: true },
    ],
    contents: [
      { id: 'localized', title: { en: 'Localized' }, description: { en: 'English copy' }, cta: { en: 'View Offer', zh: '查看优惠' }, link: 'https://example.invalid/localized' },
      { id: 'missing-locale', title: { en: 'Missing locale' }, description: { en: 'Fallback copy' }, cta: { zh: '中文按钮' }, link: 'https://example.invalid/missing-locale' },
      { id: 'malformed-cta', title: { en: 'Malformed' }, description: { en: 'Malformed copy' }, cta: { en: '   ', zh: '' }, link: 'https://example.invalid/malformed-cta' },
      { id: 'legacy', title: { en: 'Legacy' }, description: { en: 'Legacy copy' }, link: 'https://example.invalid/legacy' },
    ],
  });

  const englishPromotions = await loadActivePromotions({ locale: 'en-US', fetchImpl });
  const chinesePromotions = await loadActivePromotions({ locale: 'zh-CN', fetchImpl });

  assert.deepEqual(englishPromotions.map((promotion) => promotion.ctaLabel), ['View Offer', '中文按钮', 'GO', 'GO']);
  assert.deepEqual(chinesePromotions.map((promotion) => promotion.ctaLabel), ['查看优惠', '中文按钮', '立即前往', '立即前往']);
});
