const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '..');
const read = (relative) => fs.readFileSync(path.join(repoRoot, relative), 'utf8');
const exists = (relative) => fs.existsSync(path.join(repoRoot, relative));

const packageJson = JSON.parse(read('package.json'));
const configSource = read('docusaurus.config.mjs');

test('the site config is ESM and the CommonJS config is gone', () => {
  assert.equal(exists('docusaurus.config.js'), false);
  assert.equal(exists('docusaurus.config.mjs'), true);
  assert.equal(packageJson.type, undefined);
});

test('the Hagilight plugin is pinned to an exact version and registered', () => {
  assert.match(packageJson.dependencies['@hagicode/hagilight-docusaurus'], /^\d+\.\d+\.\d+$/);
  assert.match(configSource, /import \{ hagilightDocusaurus \} from '@hagicode\/hagilight-docusaurus';/);
  assert.match(configSource, /plugins: \[\s*hagilightDocusaurus\(/);
  assert.match(configSource, /languageSelector: \{ enabled: false \}/);
});

test('footer, analytics and promotion ownership stays with the plugin', () => {
  assert.equal(exists('src/theme/Footer'), false);
  assert.equal(exists('src/components/PromoteCard'), false);
  assert.equal(exists('src/lib/promote-loader.ts'), false);
  assert.doesNotMatch(configSource, /\bfooter:\s*\{/);
  assert.doesNotMatch(configSource, /\bgtag:/);
  assert.equal(packageJson.dependencies['@docusaurus/plugin-google-gtag'], undefined);
  assert.equal(packageJson.dependencies['react-helmet'], undefined);
});

const buildExists = (relative) => fs.existsSync(path.join(repoRoot, 'build', relative));
const buildRead = (relative) => fs.readFileSync(path.join(repoRoot, 'build', relative), 'utf8');
const countOf = (source, pattern) => (source.match(new RegExp(pattern, 'g')) || []).length;
const hasBuild = buildExists('index.html');

for (const page of ['index.html', 'Use-Dependency-Injection/index.html']) {
  test(`built ${page} loads each analytics and third-party script exactly once`, { skip: !hasBuild }, () => {
    const html = buildRead(page);
    assert.equal(countOf(html, '<footer class="hagilight-footer"'), 1);
    assert.equal(countOf(html, 'googletagmanager\\.com/gtag/js\\?id=G-EN03FMT2Q4'), 1);
    assert.equal(countOf(html, 'sdk\\.51\\.la/js-sdk-pro\\.min\\.js'), 1);
    assert.equal(countOf(html, 'LA\\.init\\(\\{id:"L6b88a5yK4h2Xnci"'), 1);
    assert.equal(countOf(html, 'sdk\\.jinrishici\\.com'), 1);
    assert.equal(countOf(html, 'adsbygoogle\\.js'), 1);
    assert.equal(countOf(html, 'pingjs\\.qq\\.com'), 1);
    assert.equal(countOf(html, 'clarity\\.ms/tag'), 1);
    assert.equal(countOf(html, '<link rel="alternate" type="application/rss\\+xml"'), 1);
  });
}

test('built home page keeps the Steam and QQ links in the footer once each', { skip: !hasBuild }, () => {
  const html = buildRead('index.html');
  const footerMatch = /<footer class="hagilight-footer"[\s\S]*?<\/footer>/.exec(html);
  assert.ok(footerMatch, 'site footer is missing from the built home page');
  const footer = footerMatch[0];
  assert.equal(countOf(html, 'store\\.steampowered\\.com/app/4625540/Hagicode/'), 1);
  assert.match(footer, /store\.steampowered\.com\/app\/4625540\/Hagicode\//);
  assert.equal(countOf(footer, 'QQ 群 610394020'), 1);
});

test('built home page has one Organization and one WebSite JSON-LD', { skip: !hasBuild }, () => {
  const html = buildRead('index.html');
  assert.equal(countOf(html, '"@type":"Organization"'), 1);
  assert.equal(countOf(html, '"@type":"WebSite"'), 1);
});

test('built rss.xml lists items with absolute links', { skip: !hasBuild }, () => {
  const rss = buildRead('rss.xml');
  const links = [...rss.matchAll(/<link>([^<]*)<\/link>/g)].map((match) => match[1]);
  assert.ok(countOf(rss, '<item>') > 0);
  for (const link of links) {
    assert.match(link, /^https:\/\/newbe\.hagicode\.com\//);
  }
});

test('built robots.txt is copied unchanged from static', { skip: !hasBuild }, () => {
  assert.equal(buildRead('robots.txt'), read('static/robots.txt'));
});

test('built sitemap lists URLs and omits the tag archive', { skip: !hasBuild }, () => {
  const sitemap = buildRead('sitemap.xml');
  assert.ok(countOf(sitemap, '<loc>') > 0);
  assert.equal(countOf(sitemap, '/tags/'), 0);
});
