/**
 * Homepage content configuration
 * Defines categories, featured documents, and learning path for the homepage
 *
 * The site publishes mirror content and its fixed pages only (see docs/Mirrors).
 * Every link here must target a mirror page or a fixed site page.
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
      title: '云原生进阶',
      description: 'Dapr, K8s, Docker',
      link: '/Mirrors',
    },
  ],

  categories: [
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
  ],

  // Empty on purpose: the homepage hides the featured section while this list is empty.
  featuredDocs: [],
};
