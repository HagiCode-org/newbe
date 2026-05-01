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
const DEFAULT_FOOTER_LOCALE = 'zh-CN';

function resolveLocalizedField(field) {
  if (typeof field === 'string') {
    return field;
  }

  if (!field || typeof field !== 'object' || Array.isArray(field)) {
    return '';
  }

  for (const candidate of [DEFAULT_FOOTER_LOCALE, 'en-US']) {
    const value = field[candidate];
    if (typeof value === 'string' && value.trim().length > 0) {
      return value;
    }
  }

  for (const value of Object.values(field)) {
    if (typeof value === 'string' && value.trim().length > 0) {
      return value;
    }
  }

  return '';
}

function resolveNewbeFooterLinks() {
  const snapshotById = new Map(snapshot.entries.map((entry) => [entry.id, entry]));

  return DEFAULT_RELATED_SITE_ORDER.flatMap((siteId) => {
    const entry = snapshotById.get(siteId);
    if (!entry || entry.id === CURRENT_SITE_ID) {
      return [];
    }

    return [{
      title: resolveLocalizedField(entry.title),
      description: resolveLocalizedField(entry.description),
      href: entry.url,
    }];
  });
}

module.exports = {
  resolveNewbeFooterLinks,
};
