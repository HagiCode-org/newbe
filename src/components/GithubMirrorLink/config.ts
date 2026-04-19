/**
 * Mirror configuration for GithubMirrorLink component.
 * The generator resolves provider-specific direct links at build time, while
 * this module merges them with the existing GitHub proxy mirrors at runtime.
 */

export type MirrorPriority = 'recommended' | 'backup' | 'official';
export type MirrorRecommendationTier = 'standard' | 'primary';

export const PRIMARY_RECOMMENDED_PROVIDER_KEY = '123pan';
export const PRIMARY_RECOMMENDATION_BADGES = ['推荐', '优先线路'] as const;

export interface ResolvedMirrorInput {
  providerKey: string;
  fullUrl: string;
  displayName?: string;
  description?: string;
  source?: string;
  status?: string;
  syncedAt?: string;
}

export interface MirrorDescriptor {
  id: string;
  providerKey: string;
  name: string;
  icon: string;
  priority: MirrorPriority;
  recommendationTier?: MirrorRecommendationTier;
  description: string;
  urlPrefix?: string;
  source: string;
  order: number;
}

export interface ResolvedMirrorLink extends MirrorDescriptor {
  fullUrl: string;
  recommended: boolean;
  recommendationTier: MirrorRecommendationTier;
  sourceLabel: string;
  syncedAt?: string;
  status?: string;
}

interface BuildMirrorSectionsInput {
  githubLink: string;
  repositoryKey?: string;
  preferredProviders?: string[];
  resolvedMirrors?: ResolvedMirrorInput[];
}

interface MirrorSectionLinks {
  recommended: ResolvedMirrorLink[];
  backup: ResolvedMirrorLink[];
  official: ResolvedMirrorLink[];
}

const officialSourceDescriptor: MirrorDescriptor = {
  id: 'official',
  providerKey: 'official',
  name: 'GitHub 原始地址',
  icon: '🔗',
  priority: 'official',
  description: '官方源',
  source: 'official',
  order: 900,
};

const recommendedMirrorDescriptors: MirrorDescriptor[] = [
  {
    id: 'ghproxy',
    providerKey: 'ghproxy',
    name: 'ghproxy.com',
    icon: '🚀',
    priority: 'recommended',
    description: '稳定高速 · GitHub 代理回退线路',
    urlPrefix: 'https://ghproxy.com/',
    source: 'default-proxy',
    order: 100,
  },
  {
    id: 'ghps',
    providerKey: 'ghps',
    name: 'ghps.cc',
    icon: '⚡',
    priority: 'recommended',
    description: '国内优化 · 速度较快',
    urlPrefix: 'https://ghps.cc/',
    source: 'default-proxy',
    order: 110,
  },
];

const backupMirrorDescriptors: MirrorDescriptor[] = [
  {
    id: 'ddlc',
    providerKey: 'ddlc',
    name: 'gh.ddlc.top',
    icon: '🌐',
    priority: 'backup',
    description: '备用线路 · 限速',
    urlPrefix: 'https://gh.ddlc.top/',
    source: 'default-proxy',
    order: 200,
  },
  {
    id: 'abskoop',
    providerKey: 'abskoop',
    name: 'github.abskoop.workers.dev',
    icon: '🔧',
    priority: 'backup',
    description: 'Cloudflare Workers · 可能不稳定',
    urlPrefix: 'https://github.abskoop.workers.dev/',
    source: 'default-proxy',
    order: 210,
  },
];

const directMirrorDescriptors: Record<string, MirrorDescriptor> = {
  '123pan': {
    id: '123pan',
    providerKey: '123pan',
    name: '123pan 分享链接',
    icon: '🏎️',
    priority: 'backup',
    recommendationTier: 'primary',
    description: '直连分享页 · 已同步到国内网盘',
    source: 'azure',
    order: 0,
  },
};

function normalizeProviderKey(providerKey: string): string {
  const normalized = providerKey.trim().toLowerCase();
  if (normalized === 'pan123') {
    return '123pan';
  }
  return normalized;
}

function getSourceLabel(source: string): string {
  switch (source) {
    case 'azure':
    case 'azure-manifest':
      return 'Azure manifest';
    case 'default-proxy':
      return '默认 GitHub 代理';
    case 'official':
      return 'GitHub 官方源';
    default:
      return source || '未知来源';
  }
}

function createResolvedMirror(
  descriptor: MirrorDescriptor,
  fullUrl: string,
  overrides?: Partial<ResolvedMirrorLink>,
): ResolvedMirrorLink {
  const recommended = overrides?.recommended ?? descriptor.priority === 'recommended';
  const recommendationTier =
    overrides?.recommendationTier ??
    (recommended && descriptor.providerKey === PRIMARY_RECOMMENDED_PROVIDER_KEY
      ? 'primary'
      : descriptor.recommendationTier ?? 'standard');

  return {
    ...descriptor,
    fullUrl,
    recommended,
    recommendationTier,
    sourceLabel: getSourceLabel(descriptor.source),
    ...overrides,
  };
}

function createDefaultMirrorLinks(githubLink: string): MirrorSectionLinks {
  return {
    recommended: recommendedMirrorDescriptors.map((descriptor) =>
      createResolvedMirror(descriptor, `${descriptor.urlPrefix}${githubLink}`),
    ),
    backup: backupMirrorDescriptors.map((descriptor) =>
      createResolvedMirror(descriptor, `${descriptor.urlPrefix}${githubLink}`),
    ),
    official: [createResolvedMirror(officialSourceDescriptor, githubLink)],
  };
}

function resolveDirectMirror(
  input: ResolvedMirrorInput,
  preferredProviders: string[],
): ResolvedMirrorLink {
  const providerKey = normalizeProviderKey(input.providerKey);
  const descriptor =
    directMirrorDescriptors[providerKey] ?? {
      id: providerKey,
      providerKey,
      name: input.displayName || providerKey,
      icon: '🪞',
      priority: 'backup',
      description: input.description || '第三方直连分享页',
      source: input.source || 'manifest',
      order: 300,
    };
  const recommended = preferredProviders.includes(providerKey);

  return createResolvedMirror(descriptor, input.fullUrl, {
    providerKey,
    name: input.displayName || descriptor.name,
    description: input.description || descriptor.description,
    priority: recommended ? 'recommended' : descriptor.priority,
    recommended,
    source: input.source || descriptor.source,
    sourceLabel: getSourceLabel(input.source || descriptor.source),
    status: input.status,
    syncedAt: input.syncedAt,
  });
}

function dedupeMirrors(mirrors: ResolvedMirrorLink[]): ResolvedMirrorLink[] {
  const seen = new Set<string>();
  return mirrors.filter((mirror) => {
    const dedupeKey = `${mirror.providerKey}:${mirror.fullUrl}`;
    if (seen.has(dedupeKey)) {
      return false;
    }
    seen.add(dedupeKey);
    return true;
  });
}

function sortMirrors(
  mirrors: ResolvedMirrorLink[],
  preferredProviders: string[],
): ResolvedMirrorLink[] {
  const preferredOrder = new Map(
    preferredProviders.map((providerKey, index) => [normalizeProviderKey(providerKey), index]),
  );

  return [...mirrors].sort((left, right) => {
    const leftPrimary = Number(isPrimaryRecommendedMirror(left));
    const rightPrimary = Number(isPrimaryRecommendedMirror(right));
    if (leftPrimary !== rightPrimary) {
      return rightPrimary - leftPrimary;
    }

    const leftPreferredOrder = preferredOrder.get(left.providerKey) ?? Number.MAX_SAFE_INTEGER;
    const rightPreferredOrder = preferredOrder.get(right.providerKey) ?? Number.MAX_SAFE_INTEGER;

    if (leftPreferredOrder !== rightPreferredOrder) {
      return leftPreferredOrder - rightPreferredOrder;
    }
    if (left.order !== right.order) {
      return left.order - right.order;
    }
    return left.name.localeCompare(right.name, 'zh-Hans-CN');
  });
}

export function isPrimaryRecommendedMirror(mirror: Pick<ResolvedMirrorLink, 'providerKey' | 'recommended'>): boolean {
  return mirror.recommended && mirror.providerKey === PRIMARY_RECOMMENDED_PROVIDER_KEY;
}

export function buildMirrorSections({
  githubLink,
  preferredProviders = [],
  resolvedMirrors = [],
}: BuildMirrorSectionsInput): MirrorSectionLinks {
  const normalizedPreferredProviders = preferredProviders.map(normalizeProviderKey);
  const defaultMirrors = createDefaultMirrorLinks(githubLink);
  const directMirrors = dedupeMirrors(
    resolvedMirrors
      .filter((mirror) => mirror?.providerKey && mirror?.fullUrl)
      .map((mirror) => resolveDirectMirror(mirror, normalizedPreferredProviders)),
  );

  const recommendedDirectMirrors = sortMirrors(
    directMirrors.filter((mirror) => mirror.priority === 'recommended'),
    normalizedPreferredProviders,
  );
  const backupDirectMirrors = sortMirrors(
    directMirrors.filter((mirror) => mirror.priority !== 'recommended'),
    normalizedPreferredProviders,
  );

  return {
    recommended: [...recommendedDirectMirrors, ...defaultMirrors.recommended],
    backup: [...backupDirectMirrors, ...defaultMirrors.backup],
    official: defaultMirrors.official,
  };
}
