// Guards the "PNG/WebP -> AVIF, referenced through the build" rule.
//
// A file in `static/` is published at a fixed URL, so a client that cached it never sees a new
// version. Raster images therefore live in `src/assets/` as AVIF and are referenced through
// webpack (markdown `![](@site/src/assets/...)` or `import`), which emits
// `assets/images/<name>-<contenthash>.avif`. `static/images/icons/` is exempt: favicons and
// manifest icons are fixed-name PNG files by design.
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const repoRoot = path.resolve(__dirname, '..');

const tracked = execFileSync('git', ['ls-files', '-z'], { cwd: repoRoot, encoding: 'utf8' })
  .split('\0')
  .filter(Boolean)
  .filter((file) => fs.existsSync(path.join(repoRoot, file)));

test('no PNG or WebP image is tracked in the site sources', () => {
  const raster = tracked.filter(
    (file) =>
      /\.(png|webp)$/i.test(file) &&
      /^(static|src|docs|i18n)\//.test(file) &&
      !file.startsWith('static/images/icons/'),
  );
  assert.deepEqual(raster, [], 'convert these with `node scripts/convert-to-avif.mjs <file>`');
});

test('site sources reference no local PNG or WebP image', () => {
  const scanned = tracked.filter(
    (file) =>
      /^(src|docs|i18n|tools)\//.test(file) &&
      /\.(md|mdx|js|jsx|ts|tsx|css|py|json)$/.test(file) &&
      !file.startsWith('tools/Newbe.Translations/') &&
      !file.startsWith('tools/MirrorDescription/'),
  );
  // External URLs (https://...) are not ours to convert; only local paths count.
  const localRaster = /(?<![:\w/.-])(?:\/|\.\/|\.\.\/|@site\/)[^\s"'()<>`]*\.(?:png|webp)\b/gi;
  const offenders = [];
  for (const file of scanned) {
    // A reference inside an HTML comment renders nothing, so it is not an image reference.
    const text = fs.readFileSync(path.join(repoRoot, file), 'utf8').replace(/<!--[\s\S]*?-->/g, '');
    for (const match of text.matchAll(localRaster)) {
      offenders.push(`${file}: ${match[0]}`);
    }
  }
  assert.deepEqual(offenders, []);
});

test('static/ holds no AVIF file', () => {
  // Anything under static/ is copied to the build verbatim, at an address that never changes.
  const staticAvif = tracked.filter((file) => /^static\/.*\.avif$/i.test(file));
  assert.deepEqual(staticAvif, [], 'move these to src/assets/ (same sub-path)');
  const onDisk = [];
  (function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (/\.avif$/i.test(entry.name)) onDisk.push(path.relative(repoRoot, full));
    }
  })(path.join(repoRoot, 'static'));
  assert.deepEqual(onDisk, []);
});

test('AVIF is referenced through the build, never by a bare static address', () => {
  // `![](/images/x.avif)`, `<img src="/images/x.avif">` or `src: '/img/x.avif'` point at static/,
  // which would keep an unchanged address (or no longer resolve at all).
  const scanned = tracked.filter(
    (file) => /^(src|docs|i18n|tools)\//.test(file) && /\.(md|mdx|js|jsx|ts|tsx|py)$/.test(file),
  );
  const bare = /(?<![\w./@-])\/(?:images|img|drawing)\/[^\s"'()<>`]*\.avif/g;
  const offenders = [];
  for (const file of scanned) {
    const text = fs.readFileSync(path.join(repoRoot, file), 'utf8');
    for (const match of text.matchAll(bare)) offenders.push(`${file}: ${match[0]}`);
  }
  assert.deepEqual(offenders, [], 'use @site/src/assets/... in markdown, or import the file');
});
