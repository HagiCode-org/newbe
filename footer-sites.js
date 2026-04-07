const snapshot = require('./src/data/footer-sites.snapshot.json');

const DEFAULT_RELATED_SITE_ORDER = [
  'hagicode-main',
  'hagicode-docs',
  'newbe-blog',
  'index-data',
  'compose-builder',
  'cost-calculator',
  'status-page',
  'awesome-design-gallery',
  'soul-builder',
  'trait-builder',
];

const CURRENT_SITE_ID = 'newbe-blog';

function resolveNewbeFooterLinks() {
  const snapshotById = new Map(snapshot.entries.map((entry) => [entry.id, entry]));

  return DEFAULT_RELATED_SITE_ORDER.flatMap((siteId) => {
    const entry = snapshotById.get(siteId);
    if (!entry || entry.id === CURRENT_SITE_ID) {
      return [];
    }

    return [{
      title: entry.title,
      description: entry.description,
      href: entry.url,
    }];
  });
}

module.exports = {
  resolveNewbeFooterLinks,
};
