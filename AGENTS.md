# Newbe - Agent Configuration

## Root Configuration

Inherits all behavior from `/AGENTS.md` at the monorepo root. Local rules extend or override the root file for this repository.

## Project Context

`newbe` is a Docusaurus-based static site served at [newbe.hagicode.com](https://newbe.hagicode.com).

## Working Directory

Run commands from `repos/newbe/`.

## Key Commands

```bash
npm install
npm run dev
npm run build
npm run typecheck
```

## Key Paths

- `docs/`: Docusaurus content
- `src/`: site customizations
- `docusaurus.config.mjs`: Docusaurus configuration (ESM; `@hagicode/hagilight-docusaurus` is ESM-only)

## Agent Guidelines

- Keep content in Markdown/MDX patterns following Docusaurus conventions.
- Production publishing is handled by GitHub Actions, not `docusaurus deploy`.
- Treat this as a static documentation site; avoid adding server-side logic.
- The footer, Google Analytics and 51LA, the promotion banner, SEO metadata and RSS come from `@hagicode/hagilight-docusaurus`; configure them through `hagilightDocusaurus()` in `docusaurus.config.mjs`, and put newbe's own footer links in `links.extraLinks`.
- Do not re-add `src/theme/Footer`, `themeConfig.footer`, `themeConfig.gtag` or a preset `gtag` option; they duplicate the plugin's footer and analytics.
- Run `npm run typecheck` to validate TypeScript before building.

## References

- `README.md`
