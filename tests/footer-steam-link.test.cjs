const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '..');

test('newbe footer keeps Steam as a repo-owned extraLinks community entry with the canonical URL', () => {
  const configSource = fs.readFileSync(path.join(repoRoot, 'docusaurus.config.mjs'), 'utf8');
  const community = /extraLinks:\s*\{[\s\S]*?community:\s*\[([^\]]*)\]/.exec(configSource);
  assert.ok(community, 'extraLinks.community is missing from docusaurus.config.mjs');
  assert.match(community[1], /label: 'Steam'/);
  assert.match(
    community[1],
    /href: 'https:\/\/store\.steampowered\.com\/app\/4625540\/Hagicode\/'/,
  );
  assert.doesNotMatch(configSource, /footer-sites|resolveNewbeFooterLinks/);
});
