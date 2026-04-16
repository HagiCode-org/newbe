const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '..');

test('newbe footer keeps Steam as a repo-owned footer entry with the canonical URL', () => {
  const configSource = fs.readFileSync(path.join(repoRoot, 'docusaurus.config.js'), 'utf8');
  const helperSource = fs.readFileSync(path.join(repoRoot, 'footer-sites.js'), 'utf8');

  assert.match(configSource, /title: 'Community'/);
  assert.match(configSource, /label: 'Steam'/);
  assert.match(
    configSource,
    /href: 'https:\/\/store\.steampowered\.com\/app\/4625540\/Hagicode\/'/,
  );
  assert.doesNotMatch(helperSource, /Steam/);
});
