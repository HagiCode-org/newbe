/**
 * Hagicode Product Configuration
 * Defines product information, links, and features for Hagicode promotion
 */

export interface HagicodeLinks {
  homepage: string;
  video: string;
  installation: string;
}

export interface HagicodeFeatures {
  title: string;
  items: string[];
}

export interface HagicodeShowcaseItem {
  id: string;
  badge: string;
  title: string;
  subtitle: string;
  description: string;
  statValue: string;
  statLabel: string;
  highlights: string[];
}

export interface HagicodeConfig {
  name: string;
  tagline: string;
  description: string;
  links: HagicodeLinks;
  features: HagicodeFeatures;
  showcase: {
    title: string;
    subtitle: string;
    items: HagicodeShowcaseItem[];
  };
  modal: {
    ctaButtons: {
      install: string;
      video: string;
    };
  };
}

/**
 * Default Hagicode configuration
 * Sync this copy against the latest Hagicode official site/docs before updating
 * promo surfaces, because mirror pages and CTA labels share this single source.
 */
export const HAGICODE_CONFIG: HagicodeConfig = {
  name: 'Hagicode',
  tagline: 'AI 驱动的代码智能助手',
  description: '连接想法与实现，支持 OpenSpec 工作流、提案驱动开发与多实例并发协作',
  links: {
    homepage: 'https://hagicode.com/',
    video: 'https://www.bilibili.com/video/BV1pirZBuEzq',
    installation: 'https://docs.hagicode.com/installation/windows-store/',
  },
  features: {
    title: '核心功能',
    items: [
      'OpenSpec 工作流 - 将需求、设计和任务沉淀为可执行提案',
      '提案驱动开发 - 把想法转化为代码改动并持续迭代',
      '多实例并发协作 - 同时推进多个开发任务，减少串行等待',
      '多轮对话与智能调试 - 结合代码审查、生成和排错加速交付',
    ],
  },
  showcase: {
    title: '三大核心特性',
    subtitle: '把智能提案、并行执行与 Hero Dungeon 工作流压缩到同一块产品展示里',
    items: [
      {
        id: 'smart',
        badge: 'SMART',
        title: '智能',
        subtitle: 'OpenSpec 工作流，让想法更快进入执行',
        description: '从想法、提案到任务拆解与归档，Hagicode 用提案驱动开发把 AI 编码流程串成完整闭环。',
        statValue: '300%',
        statLabel: '效率提升',
        highlights: ['Idea -> Proposal', 'Tasks -> Code', 'Review -> Archive'],
      },
      {
        id: 'efficient',
        badge: 'EFFICIENT',
        title: '高效',
        subtitle: '多 Agent / 多实例并行，把等待变成吞吐',
        description: 'Claude Code、Codex 等 Agent 可同时推进提案、实现、评审与修复，让额度真正持续输出。',
        statValue: '10x+',
        statLabel: '并行吞吐',
        highlights: ['Claude Code', 'Codex', 'Multi-instance'],
      },
      {
        id: 'interesting',
        badge: 'INTERESTING',
        title: '有趣',
        subtitle: 'Hero Dungeon 让协作、训练与战报更像一场冒险',
        description: '用英雄副本、队长编组和战报反馈把日常 AI 开发做成可推进、可复盘的体验。',
        statValue: 'Lv.27',
        statLabel: 'Hero Battle',
        highlights: ['英雄副本', '队长编组', '战报反馈'],
      },
    ],
  },
  modal: {
    ctaButtons: {
      install: 'Microsoft Store 安装',
      video: '实战视频',
    },
  },
};
