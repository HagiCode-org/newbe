// Test-only stand-in for `@docusaurus/Link`, which Docusaurus provides at build time.
// vitest.config.mts aliases the module here so components that link can render in jsdom.
import React from 'react';

type LinkProps = React.AnchorHTMLAttributes<HTMLAnchorElement> & { to: string };

export default function Link({ to, children, ...rest }: LinkProps): JSX.Element {
  return (
    <a href={to} {...rest}>
      {children}
    </a>
  );
}
