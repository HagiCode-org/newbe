// Guards the PWA / Windows tile wiring: the manifest and browserconfig must describe icons that
// exist with the declared size, and the site <head> must link both files.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const repoRoot = path.resolve(__dirname, '..');
const staticFile = (url) => path.join(repoRoot, 'static', url.replace(/^\//, ''));

function pngSize(file) {
  const buffer = fs.readFileSync(file);
  assert.equal(buffer.toString('latin1', 1, 4), 'PNG', `${file} is not a PNG`);
  return `${buffer.readUInt32BE(16)}x${buffer.readUInt32BE(20)}`;
}

const configSource = fs.readFileSync(path.join(repoRoot, 'docusaurus.config.mjs'), 'utf8');

test('web app manifest is complete and its icons exist at the declared size', () => {
  const manifest = JSON.parse(fs.readFileSync(staticFile('/images/icons/site.webmanifest'), 'utf8'));
  for (const key of ['name', 'short_name', 'start_url', 'display', 'theme_color', 'background_color']) {
    assert.ok(manifest[key], `manifest.${key} is empty`);
  }
  assert.ok(manifest.icons.some((icon) => icon.sizes === '192x192'), 'a 192x192 icon is required');
  assert.ok(manifest.icons.some((icon) => icon.sizes === '512x512'), 'a 512x512 icon is required');
  for (const icon of manifest.icons) {
    assert.equal(icon.type, 'image/png');
    assert.equal(pngSize(staticFile(icon.src)), icon.sizes, `${icon.src} has the wrong size`);
  }
});

test('browserconfig tile logo exists and is square', () => {
  const xml = fs.readFileSync(staticFile('/images/icons/browserconfig.xml'), 'utf8');
  const logo = /<square150x150logo src="([^"]+)"/.exec(xml);
  assert.ok(logo, 'square150x150logo is missing');
  const [w, h] = pngSize(staticFile(logo[1])).split('x');
  assert.equal(w, h);
  assert.match(xml, /<TileColor>#[0-9a-fA-F]{6}<\/TileColor>/);
});

test('site head links the manifest, touch icon, PNG favicons and the Windows tile config', () => {
  for (const href of [
    '/images/icons/site.webmanifest',
    '/images/icons/apple-touch-icon.png',
    '/images/icons/favicon-32x32.png',
    '/images/icons/favicon-16x16.png',
    '/images/icons/safari-pinned-tab.svg',
  ]) {
    assert.ok(configSource.includes(`href: '${href}'`), `headTags is missing ${href}`);
    assert.ok(fs.existsSync(staticFile(href)), `${href} does not exist`);
  }
  assert.ok(configSource.includes("content: '/images/icons/browserconfig.xml'"));
  assert.ok(fs.existsSync(path.join(repoRoot, 'static/images/icons/favicon.ico')));
});
