## 1. Footer Popup Removal

- [ ] 1.1 Update `src/theme/DocItem/Footer/index.js` to remove `HagicodeModal`, `shouldShowModal()`, and the modal state/effect flow while preserving the existing Footer content, WeChat block, and `HagicodeAd`.
- [ ] 1.2 Delete `src/components/HagicodeModal/index.tsx` and `src/components/HagicodeModal/index.module.css`, then verify no remaining runtime imports reference the removed modal component.

## 2. Shared Promo Config Cleanup

- [ ] 2.1 Remove `modal.storageKey` from the `HagicodeConfig` type and `HAGICODE_CONFIG`, and delete `shouldShowModal()` plus `markTodayVisited()` from `src/components/HagicodeConfig.ts`.
- [ ] 2.2 Confirm `HagicodeAd`, `HagicodeAdHeader`, and `HagicodeAdBanner` still compile against the cleaned shared config and continue using the existing CTA labels, links, and feature copy.

## 3. Verification

- [ ] 3.1 Run a repository search for `HagicodeModal`, `shouldShowModal`, `markTodayVisited`, and `hagicode_last_visit_date` to confirm the first-visit popup path has been removed from `src/`.
- [ ] 3.2 Run `npm run typecheck` and `npm run build` to verify the Docusaurus site still compiles and the remaining explicit HagiCode promo surfaces render without the modal flow.

## 4. Follow-up Documentation

- [ ] 4.1 Update any inline comments or nearby implementation notes that still describe a first-visit HagiCode popup so the source matches the new non-blocking promo behavior.
