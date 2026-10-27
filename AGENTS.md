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
npm test
node --test tests/*.test.cjs
```

Requires Node.js 24+. The `node --test` suites (plugin integration and footer checks) have no npm script. Other scripts: `npm run serve` (preview a built site), `npm run clear`, `npm run write-heading-ids`, `npm run write-translations`.

## Key Paths

- `docs/`: Docusaurus content; `docs/Mirrors/` is generated output
- `i18n/zh/`: Chinese translations
- `src/`: site customizations
- `tests/`: `node:test` suites (`*.test.cjs`) guarding the HagiLight plugin integration
- `tools/`: Python (Pipenv/invoke) mirror generator, with its own `unittest` tests in `tools/tests/` (modules import from `tools/`, so run from there, e.g. `python -m unittest discover -s tests`)
- `.github/workflows/`: `newbe-deploy-gh-pages.yml` (deploy) and `mirror-update.yml` (daily mirror regeneration that commits to `main`); `compress-images.yml` (image compression on PRs/pushes touching jpg/png/webp) and `labeler.yml` (PR labeler)
- `docusaurus.config.mjs`: Docusaurus configuration (ESM; `@hagicode/hagilight-docusaurus` is ESM-only)

## Agent Guidelines

- Keep content in Markdown/MDX patterns following Docusaurus conventions.
- Production publishing is handled by GitHub Actions, not `docusaurus deploy`.
- Treat this as a static documentation site; avoid adding server-side logic.
- The footer, Google Analytics and 51LA, the promotion banner, SEO metadata and RSS come from `@hagicode/hagilight-docusaurus`; configure them through `hagilightDocusaurus()` in `docusaurus.config.mjs`, and put newbe's own footer links in `links.extraLinks`.
- Do not re-add `src/theme/Footer`, `themeConfig.footer`, `themeConfig.gtag` or a preset `gtag` option; they duplicate the plugin's footer and analytics.
- Run `npm run typecheck` to validate TypeScript before building.
- Do not hand-edit `docs/Mirrors/`; change the generator in `tools/` (or its definition JSON) and let `mirror-update` regenerate the pages. `build/` and `.docusaurus/` are gitignored output.

## PostHog Events

Site events go through `src/lib/posthog-events.ts` (`captureSiteEvent`). It sends nothing when `window.posthog` is missing, the visitor has opted out, or the name is not in `SITE_POSTHOG_EVENTS`, and it never throws.

| Event | Fires when | Properties |
|-------|------------|------------|
| `download_mirror_clicked` | A mirror card's copy resolves (`handleCopy`), or a mirror is opened (`handleOpen`) | `mirror` (provider key), `action` (`copy` or `open`), `recommended` (boolean) |

- No event carries a URL, `fullUrl` or any URL text.
- Deduplication: `HagicodeAdBanner` and `HagicodeRecommendation` CTA links carry `gaEventAttributes`, so a click there can also produce hagilight's `cta_click`. Those links have no business event, so there is no double count. Mirror card buttons carry no `data-ga-*` marker, so `download_mirror_clicked` is their only record. Dashboards must not add `download_mirror_clicked` to `cta_click` counts.

## References

- `README.md`
