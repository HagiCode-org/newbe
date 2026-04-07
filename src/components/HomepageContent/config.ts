/**
 * Homepage content configuration
 * Defines categories, featured documents, and learning path for the homepage
 */

export interface FeaturedDoc {
  title: string;
  path: string;
  description?: string;
}

export interface Category {
  id: string;
  icon: string;
  title: string;
  description: string;
  link: string;
  featuredDocs: FeaturedDoc[];
}

export interface LearningPathStep {
  step: number;
  title: string;
  description: string;
  link?: string;
}

export interface HomepageContentConfig {
  learningPath: LearningPathStep[];
  categories: Category[];
  featuredDocs: Array<FeaturedDoc & { badge?: string }>;
}

export const homepageContent: HomepageContentConfig = {
  learningPath: [
    {
      step: 1,
      title: '.NET 基础',
      description: 'C# 特性与语法',
      link: '/Mic',
    },
    {
      step: 2,
      title: '云原生进阶',
      description: 'Dapr, K8s, Docker',
      link: '/Mirrors',
    },
    {
      step: 3,
      title: '性能调优',
      description: '优化技巧与工具',
      link: '/Mic/0018-How-to-Use-DotTrace',
    },
    {
      step: 4,
      title: '架构设计',
      description: '系统设计模式',
      link: '/Projects/Newbe.Claptrap/Get-Started-1',
    },
  ],

  categories: [
    {
      id: 'mic',
      icon: '📝',
      title: '技术短文',
      description: 'C# 进阶特性、Expression Trees、性能优化实践',
      link: '/Mic',
      featuredDocs: [
        {
          title: 'Cancellation Tokens 性能优化',
          path: '/Mic/0006-Performance-enhancement-for-web-by-cancellation-token',
        },
        {
          title: 'Expression Trees 实战',
          path: '/Mic/0017-Using-Expression-Tree-To-Build-Delegate',
        },
        {
          title: 'StringPool 内存优化',
          path: '/Mic/0009-StringPool-For-Your-Code',
        },
      ],
    },
    {
      id: 'mirrors',
      icon: '🔄',
      title: '开源镜像',
      description: '.NET Core、Dapr、Kubernetes 等技术文档镜像',
      link: '/Mirrors',
      featuredDocs: [
        {
          title: 'Dapr 文档镜像',
          path: '/Mirrors/Mirrors-Dapr',
        },
        {
          title: 'Kubernetes (k3s)',
          path: '/Mirrors/Mirrors-k3s',
        },
        {
          title: 'Minikube 指南',
          path: '/Mirrors/Mirrors-minikube',
        },
      ],
    },
    {
      id: 'tutorial',
      icon: '📚',
      title: '教程',
      description: '从零开始系列教程和最佳实践指南',
      link: '/Tutorial',
      featuredDocs: [
        {
          title: '搭建你的博客',
          path: '/Tutorial/Build-Your-Own-Blog/Build-Your-Own-Blog-For-Free',
        },
        {
          title: '依赖注入使用',
          path: '/Use-Dependency-Injection',
        },
        {
          title: 'Reactive in Server',
          path: '/Tutorial/Reactive-in-Server/Reactive-In-Server-1',
        },
      ],
    },
    {
      id: 'projects',
      icon: '🚀',
      title: '项目文档',
      description: 'Newbe.Claptrap、Newbe.Mahua 等项目文档',
      link: '/Projects',
      featuredDocs: [
        {
          title: 'Newbe.Claptrap',
          path: '/Projects/Newbe.Claptrap/Get-Started-1',
        },
        {
          title: 'Newbe.Mahua',
          path: '/Projects/Newbe.Mahua/Begin-First-Plugin-With-Mahua',
        },
        {
          title: 'Newbe.ObjectVisitor',
          path: '/Projects/Newbe.ObjectVisitor/001-my-fisrt-object-visitor',
        },
      ],
    },
  ],

  featuredDocs: [
    {
      title: 'Cancellation Tokens 性能优化',
      description: '在 Web 应用中使用 Cancellation Tokens 提升性能',
      path: '/Mic/0006-Performance-enhancement-for-web-by-cancellation-token',
      badge: '🔥 热门',
    },
    {
      title: 'Expression Trees 实战',
      description: '深入了解表达式树的使用场景和最佳实践',
      path: '/Mic/0017-Using-Expression-Tree-To-Build-Delegate',
      badge: '⭐ 推荐',
    },
    {
      title: 'Docker/K8s 容器化实践',
      description: '使用 Minikube 搭建本地 Kubernetes 环境',
      path: '/Mic/0007-Setup-K8s-With-Minikube',
      badge: '🚀 实战',
    },
    {
      title: 'ASP.NET Core 性能调优',
      description: '使用 DotTrace 进行性能分析',
      path: '/Mic/0018-How-to-Use-DotTrace',
      badge: '💡 技巧',
    },
  ],
};
