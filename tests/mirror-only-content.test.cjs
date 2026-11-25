// Guards the mirror-only content rule: the site publishes docs/Mirrors and the homepage
// (docs/intro.md), no blog sections, and no AVIF under src/assets/ that nothing references.
// A removed section or an orphaned image fails here, naming the offending path.
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const repoRoot = path.resolve(__dirname, '..');

const list = (args) =>
  execFileSync('git', ['ls-files', '-z', ...args], { cwd: repoRoot, encoding: 'utf8' })
    .split('\0')
    .filter(Boolean)
    .filter((file) => fs.existsSync(path.join(repoRoot, file)));

// Text sources that can reference an image: tracked files only, as the reference rule states.
const tracked = list([]);
// Images: tracked plus new files that git does not ignore, so an AVIF dropped in without `git add` is still checked.
const candidates = list(['--cached', '--others', '--exclude-standard']);

const TEXT_SOURCES = [/^docs\//, /^src\//, /^i18n\//, /^tools\//, /^docusaurus\.config\.mjs$/];
const ALLOWED_DOCS_CHILDREN = ['intro.md', 'Mirrors'];

const escapeRegExp = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

test('docs/ holds only the homepage and the mirror pages', () => {
  const children = fs
    .readdirSync(path.join(repoRoot, 'docs'))
    .filter((name) => !ALLOWED_DOCS_CHILDREN.includes(name));
  assert.deepEqual(
    children,
    [],
    `remove these from docs/: only ${ALLOWED_DOCS_CHILDREN.join(' and ')} may be published`,
  );
});

test('every AVIF under src/assets/ is referenced by name from a tracked text source', () => {
  const texts = tracked
    .filter((file) => TEXT_SOURCES.some((root) => root.test(file)) && !file.startsWith('src/assets/'))
    .map((file) => fs.readFileSync(path.join(repoRoot, file)))
    .filter((buffer) => !buffer.subarray(0, 8000).includes(0)) // skip binary files
    .map((buffer) => buffer.toString('utf8'));

  const orphans = candidates
    .filter((file) => file.startsWith('src/assets/') && /\.avif$/i.test(file))
    .filter((file) => {
      // Match the bare file name, as the build and the mirror pages write it.
      const name = path.posix.basename(file);
      const pattern = new RegExp(`(?<![\\w.-])${escapeRegExp(name)}(?![\\w-])`);
      return !texts.some((text) => pattern.test(text));
    });

  assert.deepEqual(
    orphans,
    [],
    'no text source references these images: delete them, or reference them through @site/src/assets/...',
  );
});
