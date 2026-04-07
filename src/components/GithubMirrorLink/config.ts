/**
 * Mirror configuration for GithubMirrorLink component
 * Mirrors are grouped by priority: recommended, backup, and official source
 */

export interface MirrorConfig {
  /** Unique identifier for the mirror */
  id: string;
  /** Display name of the mirror service */
  name: string;
  /** URL prefix to prepend to the GitHub link */
  urlPrefix: string;
  /** Emoji or icon to represent the mirror */
  icon: string;
  /** Priority level for grouping */
  priority: 'recommended' | 'backup' | 'official';
  /** Short description of the mirror characteristics */
  description: string;
}

/**
 * Official GitHub source (original link)
 */
export const officialSource: MirrorConfig = {
  id: 'official',
  name: 'GitHub 原始地址',
  urlPrefix: '',
  icon: '🔗',
  priority: 'official',
  description: '官方源',
};

/**
 * Recommended mirrors - stable and fast
 */
export const recommendedMirrors: MirrorConfig[] = [
  {
    id: 'ghproxy',
    name: 'ghproxy.com',
    urlPrefix: 'https://ghproxy.com/',
    icon: '🚀',
    priority: 'recommended',
    description: '稳定高速 · 国内外均可访问',
  },
  {
    id: 'ghps',
    name: 'ghps.cc',
    urlPrefix: 'https://ghps.cc/',
    icon: '⚡',
    priority: 'recommended',
    description: '国内优化 · 速度较快',
  },
];

/**
 * Backup mirrors - alternative options
 */
export const backupMirrors: MirrorConfig[] = [
  {
    id: 'ddlc',
    name: 'gh.ddlc.top',
    urlPrefix: 'https://gh.ddlc.top/',
    icon: '🌐',
    priority: 'backup',
    description: '备用线路 · 限速',
  },
  {
    id: 'abskoop',
    name: 'github.abskoop.workers.dev',
    urlPrefix: 'https://github.abskoop.workers.dev/',
    icon: '🔧',
    priority: 'backup',
    description: 'Cloudflare Workers · 可能不稳定',
  },
];

/**
 * All mirrors combined (excluding official source)
 */
export const allMirrors: MirrorConfig[] = [
  ...recommendedMirrors,
  ...backupMirrors,
];

/**
 * Get full mirror URL by combining prefix with GitHub link
 */
export function getMirrorUrl(mirror: MirrorConfig, githubLink: string): string {
  return mirror.urlPrefix + githubLink;
}
