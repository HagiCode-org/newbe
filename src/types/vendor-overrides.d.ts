declare module 'react-dom' {
  import type { ReactNode, ReactPortal } from 'react';

  export function createPortal(
    children: ReactNode,
    container: Element | DocumentFragment,
  ): ReactPortal;
}

declare module '@docusaurus/Link' {
  import type { JSX, ReactNode } from 'react';

  export interface LinkProps {
    to?: string;
    href?: string;
    className?: string;
    children?: ReactNode;
    [key: string]: unknown;
  }

  export default function Link(props: LinkProps): JSX.Element;
}

declare module '@docusaurus/useDocusaurusContext' {
  export default function useDocusaurusContext(): {
    i18n: {
      currentLocale?: string;
    };
  };
}

declare module '*.module.css' {
  const classes: Record<string, string>;
  export default classes;
}
